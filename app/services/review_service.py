from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from app.models.review import Review
from app.models.order import Order, OrderItem
from app.models.dish import Dish
from app.models.events import PreferenceEvent

async def create_review(
    db: AsyncSession,
    user_id: int,
    order_id: int,
    dish_id: int,
    rating: int,
    comment: str | None,
    tags: list[str],
) -> Review:
    # 校验订单归属且已完成（固定决策：只有 completed 可评价）
    order_res = await db.execute(select(Order).where(Order.id == order_id, Order.user_id == user_id))
    order = order_res.scalar_one_or_none()
    if not order:
        raise ValueError("order_not_found")
    if order.status != "completed":
        raise ValueError("order_not_completed")

    # 校验该菜在该订单里
    item_res = await db.execute(select(OrderItem).where(OrderItem.order_id == order_id, OrderItem.dish_id == dish_id))
    if not item_res.scalar_one_or_none():
        raise ValueError("dish_not_in_order")

    rv = Review(user_id=user_id, order_id=order_id, dish_id=dish_id, rating=rating, comment=comment, tags=tags or [])
    db.add(rv)

    try:
        await db.commit()
        await db.refresh(rv)
    except IntegrityError:
        await db.rollback()
        raise ValueError("review_already_exists")

    # 更新菜品评分（固定决策：增量平均）
    dish_res = await db.execute(select(Dish).where(Dish.id == dish_id))
    dish = dish_res.scalar_one_or_none()
    if dish:
        old_count = int(dish.rating_count)
        old_avg = float(dish.rating_avg)
        new_count = old_count + 1
        new_avg = (old_avg * old_count + rating) / new_count
        dish.rating_count = new_count
        dish.rating_avg = round(new_avg, 1)
        db.add(dish)

    # 偏好事件（评论）
    db.add(PreferenceEvent(
        user_id=user_id,
        event_type="review",
        payload={"order_id": int(order_id), "dish_id": int(dish_id), "rating": int(rating), "tags": tags or []}
    ))

    await db.commit()
    return rv

async def list_reviews_by_dish(db: AsyncSession, dish_id: int, limit: int = 20, offset: int = 0) -> tuple[list[Review], int]:
    total_res = await db.execute(select(func.count()).select_from(Review).where(Review.dish_id == dish_id))
    total = int(total_res.scalar() or 0)

    res = await db.execute(
        select(Review)
        .where(Review.dish_id == dish_id)
        .order_by(Review.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(res.scalars().all()), total
