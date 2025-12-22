from __future__ import annotations

from datetime import datetime
from fastapi import HTTPException
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.models.address import UserAddress
from app.models.dish import Dish, DishSpec
from app.models.events import PreferenceEvent
from app.models.order import Order, OrderItem
from app.models.user import User
from app.schemas.order import OrderCreateIn


# -----------------------------
# 订单上下文（固定决策）
# -----------------------------
def _time_bucket_local() -> str:
    # 固定决策：以服务端本地时间划分餐段（你后续可替换为用户时区/前端上报）
    now = datetime.now()
    h = now.hour
    if 5 <= h < 11:
        return "breakfast"
    if 11 <= h < 15:
        return "lunch"
    if 15 <= h < 22:
        return "dinner"
    return "late_night"


# -----------------------------
# 规格校验与价格增量
# -----------------------------
def _build_spec_index(spec_defs: list[DishSpec]) -> dict[str, list[dict]]:
    """
    返回：{spec_name: [ {name, price?}, ... ]}
    """
    idx: dict[str, list[dict]] = {}
    for s in spec_defs:
        values = s.spec_values or []
        # 只保留 dict 项，保证健壮性
        cleaned = [v for v in values if isinstance(v, dict) and isinstance(v.get("name"), str)]
        idx[s.spec_name] = cleaned
    return idx


def _validate_specs(spec_defs: list[DishSpec], selected_specs: dict) -> None:
    """
    固定决策：
    - selected_specs 的 key 必须在 dish_specs.spec_name 中
    - selected_specs 的 value 必须命中 spec_values[].name
    """
    selected_specs = selected_specs or {}
    spec_index = _build_spec_index(spec_defs)

    for k, v in selected_specs.items():
        if k not in spec_index:
            raise ValueError("invalid_spec_name")
        allowed_names = [opt["name"] for opt in spec_index[k]]
        if v not in allowed_names:
            raise ValueError("invalid_spec_value")


def _spec_price_delta(spec_defs: list[DishSpec], selected_specs: dict) -> float:
    """
    固定决策：
    - spec_values[] 可以包含 price（数值），作为加价增量
    - 所有选中规格的 price 叠加
    """
    selected_specs = selected_specs or {}
    spec_index = _build_spec_index(spec_defs)

    delta = 0.0
    for k, v in selected_specs.items():
        for opt in spec_index.get(k, []):
            if opt.get("name") == v:
                try:
                    delta += float(opt.get("price") or 0.0)
                except (TypeError, ValueError):
                    delta += 0.0
                break
    return float(delta)


# -----------------------------
# 订单创建
# -----------------------------



def _time_bucket(dt: datetime) -> str:
    h = dt.hour
    if 5 <= h < 11:
        return "breakfast"
    if 11 <= h < 15:
        return "lunch"
    if 17 <= h < 22:
        return "dinner"
    return "late_night"


async def create_order(
    db: AsyncSession,
    user_id: int,
    address_id: int | None = None,
    items: list | None = None,
    note: str | None = None,
    data: Any | None = None,
    **kwargs,
) -> Order:
    """
    强兼容版（最终定稿）：
    - routes 传关键字参数：user_id/address_id/items/note
    - 也兼容传 data（具有 address_id/items/note 属性）
    - items 支持 dict 或对象（Pydantic/Schema）
    - 自适应事务，避免 SQLAlchemy 2.x autobegin 冲突
    """

    # 1) 统一入参来源
    if data is not None:
        if address_id is None:
            address_id = int(getattr(data, "address_id"))
        if items is None:
            items = list(getattr(data, "items"))
        if note is None:
            note = getattr(data, "note", None)

    if address_id is None:
        raise HTTPException(status_code=400, detail="address_id_required")
    if not items:
        raise HTTPException(status_code=400, detail="empty_items")

    # 2) 标准化 items（解决 dict/object 两种形态）
    norm_items: list[dict[str, Any]] = []
    for x in items:
        if isinstance(x, dict):
            dish_id = x.get("dish_id")
            quantity = x.get("quantity", 1)
            selected_specs = x.get("selected_specs") or {}
        else:
            dish_id = getattr(x, "dish_id", None)
            quantity = getattr(x, "quantity", 1)
            selected_specs = getattr(x, "selected_specs", None) or {}

        if dish_id is None:
            raise HTTPException(status_code=400, detail="dish_id_required")

        norm_items.append(
            {
                "dish_id": int(dish_id),
                "quantity": int(quantity),
                "selected_specs": selected_specs,
            }
        )

    now = datetime.utcnow()
    context_snapshot: dict[str, Any] = {
        "created_at_utc": now.isoformat(),
        "time_bucket": _time_bucket(now),
        "weekday": now.weekday(),
    }

    # 3) 自适应事务（避免 transaction already begun）
    tx = (db.begin_nested() if db.in_transaction() else db.begin())
    async with tx:
        # 3.1 地址校验
        addr = await db.get(UserAddress, int(address_id))
        if not addr:
            raise HTTPException(status_code=404, detail="address_not_found")
        if int(getattr(addr, "user_id")) != int(user_id):
            raise HTTPException(status_code=403, detail="address_forbidden")

        # 3.2 菜品校验
        dish_ids = [it["dish_id"] for it in norm_items]
        res = await db.execute(select(Dish).where(Dish.id.in_(dish_ids)))
        dish_list = list(res.scalars().all())
        dish_map = {int(d.id): d for d in dish_list}

        missing = [did for did in dish_ids if did not in dish_map]
        if missing:
            raise HTTPException(status_code=400, detail={"code": "dish_not_found", "ids": missing})

        for d in dish_list:
            if getattr(d, "status", "on_sale") != "on_sale":
                raise HTTPException(status_code=400, detail={"code": "dish_not_on_sale", "dish_id": int(d.id)})

        # 3.3 总价（暂不处理规格加价）
        total = 0.0
        for it in norm_items:
            d = dish_map[it["dish_id"]]
            total += float(getattr(d, "price")) * int(it["quantity"])

        # 3.4 创建订单
        order = Order(
            user_id=int(user_id),
            total_amount=total,
            status="pending",
            note=note,
            context_snapshot=context_snapshot,
        )

        if hasattr(order, "address_id"):
            setattr(order, "address_id", int(address_id))

        db.add(order)
        await db.flush()

        # 3.5 创建订单明细（快照）
        for it in norm_items:
            d = dish_map[it["dish_id"]]
            oi = OrderItem(
                order_id=int(order.id),
                dish_id=int(d.id),
                dish_name=getattr(d, "name", ""),
                quantity=int(it["quantity"]),
                price_snapshot=float(getattr(d, "price")),
                selected_specs=it["selected_specs"],
            )
            db.add(oi)

        await db.flush()
        await db.refresh(order)
        return order




# -----------------------------
# 状态流转（支付/完成/取消）
# -----------------------------

async def set_order_status(
    db: AsyncSession,
    user_id: int,
    order_id: int,
    new_status: str,
) -> Order:
    """
    固定决策：状态机
    - pending -> paid / cancelled
    - paid -> completed
    - completed/cancelled 终态不可变更
    且：
    - pending -> paid 时：增加 dishes.sales_count（按 order_items.quantity）
    - 记录 preference_events
    """

    allowed = {
        "pending": {"paid", "cancelled"},
        "paid": {"completed"},
        "completed": set(),
        "cancelled": set(),
    }
    if new_status not in {"pending", "paid", "completed", "cancelled"}:
        raise ValueError("invalid_status")

    # 自适应事务：避免 SQLAlchemy 2.x autobegin 冲突
    tx = (db.begin_nested() if db.in_transaction() else db.begin())
    async with tx:
        res = await db.execute(
            select(Order).where(Order.id == int(order_id), Order.user_id == int(user_id))
        )
        order = res.scalar_one_or_none()
        if not order:
            raise ValueError("order_not_found")

        if new_status not in allowed.get(order.status, set()):
            raise ValueError("invalid_status_transition")

        prev = order.status
        order.status = new_status
        db.add(order)

        # pending -> paid：销量入账（固定决策：支付时才计销量）
        if prev == "pending" and new_status == "paid":
            items_res = await db.execute(
                select(OrderItem).where(OrderItem.order_id == int(order.id))
            )
            items = list(items_res.scalars().all())

            # 聚合每个 dish_id 的数量
            agg: dict[int, int] = {}
            for it in items:
                did = int(it.dish_id)
                agg[did] = agg.get(did, 0) + int(it.quantity)

            for dish_id, qty in agg.items():
                await db.execute(
                    update(Dish)
                    .where(Dish.id == int(dish_id))
                    .values(sales_count=Dish.sales_count + int(qty))
                )

            db.add(
                PreferenceEvent(
                    user_id=int(user_id),
                    event_type="order_paid",
                    payload={"order_id": int(order.id), "total_amount": float(order.total_amount)},
                )
            )

        # paid -> completed：完成事件
        if prev == "paid" and new_status == "completed":
            db.add(
                PreferenceEvent(
                    user_id=int(user_id),
                    event_type="order_completed",
                    payload={"order_id": int(order.id), "total_amount": float(order.total_amount)},
                )
            )

        # pending -> cancelled：取消事件
        if prev == "pending" and new_status == "cancelled":
            db.add(
                PreferenceEvent(
                    user_id=int(user_id),
                    event_type="order_cancelled",
                    payload={"order_id": int(order.id)},
                )
            )

        # 刷新最新状态
        await db.flush()
        await db.refresh(order)
        return order
