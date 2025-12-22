from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.core.deps import require_user
from app.models.user import User
from app.models.order import Order, OrderItem
from app.schemas.order import OrderCreateIn, OrderCreateOut, OrderListOut, OrderListItem, OrderDetailOut, OrderItemOut
from app.services.order_service import create_order, set_order_status

router = APIRouter(prefix="/orders")

@router.post("", response_model=OrderCreateOut)
async def create(payload: OrderCreateIn, user: User = Depends(require_user), db: AsyncSession = Depends(get_db)):
    try:
        order = await create_order(
            db=db,
            user_id=int(user.id),
            address_id=payload.address_id,
            note=payload.note,
            items=[it.model_dump() for it in payload.items],
        )
        return OrderCreateOut(order_id=int(order.id), status=order.status, total_amount=float(order.total_amount))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=OrderListOut)
async def list_orders(user: User = Depends(require_user), db: AsyncSession = Depends(get_db)):
    total_res = await db.execute(select(func.count()).select_from(Order).where(Order.user_id == int(user.id)))
    total = int(total_res.scalar() or 0)

    res = await db.execute(
        select(Order)
        .where(Order.user_id == int(user.id))
        .order_by(Order.created_at.desc())
        .limit(50)
    )
    items = []
    for o in res.scalars().all():
        items.append(OrderListItem(
            id=int(o.id),
            status=o.status,
            total_amount=float(o.total_amount),
            created_at=str(o.created_at) if o.created_at else None
        ))
    return OrderListOut(items=items, total=total)

@router.get("/{order_id}", response_model=OrderDetailOut)
async def detail(order_id: int, user: User = Depends(require_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Order).where(Order.id == order_id, Order.user_id == int(user.id)))
    o = res.scalar_one_or_none()
    if not o:
        raise HTTPException(status_code=404, detail="order_not_found")

    items_res = await db.execute(select(OrderItem).where(OrderItem.order_id == int(o.id)))
    items = []
    for it in items_res.scalars().all():
        items.append(OrderItemOut(
            id=int(it.id),
            dish_id=int(it.dish_id),
            dish_name=it.dish_name,
            quantity=int(it.quantity),
            price_snapshot=float(it.price_snapshot),
            selected_specs=it.selected_specs or {}
        ))

    return OrderDetailOut(
        id=int(o.id),
        status=o.status,
        total_amount=float(o.total_amount),
        note=o.note,
        created_at=str(o.created_at) if o.created_at else None,
        address_snapshot=o.address_snapshot or {},
        items=items
    )

@router.post("/{order_id}/pay")
async def pay(order_id: int, user: User = Depends(require_user), db: AsyncSession = Depends(get_db)):
    try:
        o = await set_order_status(db, int(user.id), order_id, "paid")
        return {"status": o.status}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{order_id}/complete")
async def complete(order_id: int, user: User = Depends(require_user), db: AsyncSession = Depends(get_db)):
    try:
        o = await set_order_status(db, int(user.id), order_id, "completed")
        return {"status": o.status}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
