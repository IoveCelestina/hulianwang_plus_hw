import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.models.cart import Cart, CartItem
from app.models.dish import Dish

def _spec_key(selected_specs: dict) -> str:
    # 固定决策：spec 合并键 = JSON 排序字符串
    return json.dumps(selected_specs or {}, ensure_ascii=False, sort_keys=True)

async def get_or_create_cart(db: AsyncSession, user_id: int) -> Cart:
    res = await db.execute(select(Cart).where(Cart.user_id == user_id))
    cart = res.scalar_one_or_none()
    if cart:
        return cart
    cart = Cart(user_id=user_id, updated_at=datetime.utcnow())
    db.add(cart)
    await db.commit()
    await db.refresh(cart)
    return cart

async def get_cart_view(db: AsyncSession, user_id: int) -> tuple[list[dict], float]:
    cart = await get_or_create_cart(db, user_id)
    items_res = await db.execute(select(CartItem).where(CartItem.cart_id == cart.id))
    items = list(items_res.scalars().all())
    dish_ids = [it.dish_id for it in items]
    dish_map = {}
    if dish_ids:
        dish_res = await db.execute(select(Dish).where(Dish.id.in_(dish_ids)))
        dish_map = {int(d.id): d for d in dish_res.scalars().all()}

    view_items = []
    total = 0.0
    for it in items:
        dish = dish_map.get(int(it.dish_id))
        if not dish:
            continue
        price = float(dish.price)
        line = price * int(it.quantity)
        total += line
        view_items.append({
            "id": int(it.id),
            "dish_id": int(it.dish_id),
            "dish_name": dish.name,
            "price": price,
            "quantity": int(it.quantity),
            "selected_specs": it.selected_specs or {}
        })
    return view_items, round(total, 2)

async def add_to_cart(db: AsyncSession, user_id: int, dish_id: int, quantity: int, selected_specs: dict) -> None:
    cart = await get_or_create_cart(db, user_id)

    # 校验菜品在售
    dish_res = await db.execute(select(Dish).where(Dish.id == dish_id))
    dish = dish_res.scalar_one_or_none()
    if not dish or dish.status != "on_sale":
        raise ValueError("dish_not_available")

    items_res = await db.execute(select(CartItem).where(CartItem.cart_id == cart.id, CartItem.dish_id == dish_id))
    items = list(items_res.scalars().all())
    skey = _spec_key(selected_specs)

    for it in items:
        if _spec_key(it.selected_specs or {}) == skey:
            it.quantity = int(it.quantity) + int(quantity)
            db.add(it)
            await db.commit()
            return

    db.add(CartItem(cart_id=cart.id, dish_id=dish_id, quantity=quantity, selected_specs=selected_specs or {}))
    await db.commit()

async def update_cart_item(db: AsyncSession, user_id: int, item_id: int, quantity: int | None, selected_specs: dict | None) -> None:
    cart = await get_or_create_cart(db, user_id)
    res = await db.execute(select(CartItem).where(CartItem.id == item_id, CartItem.cart_id == cart.id))
    it = res.scalar_one_or_none()
    if not it:
        raise ValueError("cart_item_not_found")
    if quantity is not None:
        it.quantity = int(quantity)
    if selected_specs is not None:
        it.selected_specs = selected_specs
    db.add(it)
    await db.commit()

async def delete_cart_item(db: AsyncSession, user_id: int, item_id: int) -> None:
    cart = await get_or_create_cart(db, user_id)
    res = await db.execute(select(CartItem).where(CartItem.id == item_id, CartItem.cart_id == cart.id))
    it = res.scalar_one_or_none()
    if not it:
        raise ValueError("cart_item_not_found")
    await db.delete(it)
    await db.commit()
