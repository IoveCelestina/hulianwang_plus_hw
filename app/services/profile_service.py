from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.models.user_preferences import UserPreferences
from app.models.order import OrderItem
from app.models.dish import Dish

def _bump_counter(d: dict, key: str, inc: float) -> dict:
    d[key] = float(d.get(key, 0.0)) + float(inc)
    return d

async def update_profile_from_recent_orders(db: AsyncSession, user_id: int, last_n_items: int = 50) -> None:
    # 固定决策：每次下单完成后可调用（你二期可做异步 job）
    pref_res = await db.execute(select(UserPreferences).where(UserPreferences.user_id == user_id))
    pref = pref_res.scalar_one_or_none()
    if not pref:
        pref = UserPreferences(user_id=user_id, explicit_tags=[], implicit_profile={}, dietary_restrictions=[])
        db.add(pref)
        await db.commit()
        await db.refresh(pref)

    # 取最近 N 个 order_items（简化：按 order_items id 倒序近似）
    items_res = await db.execute(
        select(OrderItem).where(OrderItem.order_id.in_(
            select(OrderItem.order_id).where(OrderItem.order_id != None)  # noqa
        ))
    )
    # 为避免复杂 join，一期不在这里做全量聚合；画像更新由评论触发即可。
    # 我这里保留接口形态，避免后续你扩展时重构路由。
    pref.last_updated = datetime.utcnow()
    db.add(pref)
    await db.commit()
