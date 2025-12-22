from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.core.deps import require_user
from app.models.user import User
from app.models.dish import Category
from app.schemas.dish import CategoryOut, DishListOut, DishListItem, DishDetailOut, DishSpecOut
from app.services.dish_service import list_dishes, get_dish_detail, recommend_home, compute_highlights

router = APIRouter(prefix="/dishes")

@router.get("/categories", response_model=list[CategoryOut])
async def categories(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Category).order_by(Category.sort_order.asc(), Category.id.asc()))
    return [CategoryOut(id=int(c.id), name=c.name, sort_order=int(c.sort_order or 0)) for c in res.scalars().all()]

@router.get("", response_model=DishListOut)
async def dishes(
    db: AsyncSession = Depends(get_db),
    category_id: int | None = Query(default=None),
    keyword: str | None = Query(default=None),
    status: str = Query(default="on_sale"),
):
    items = await list_dishes(db, category_id=category_id, keyword=keyword, status=status)
    out = []
    for d in items:
        out.append(DishListItem(
            id=int(d.id),
            name=d.name,
            price=float(d.price),
            image_url=d.image_url,
            status=d.status,
            rating_avg=float(d.rating_avg),
            rating_count=int(d.rating_count),
            sales_count=int(d.sales_count),
            ai_highlights=compute_highlights(d.ai_metadata or {})
        ))
    return DishListOut(items=out, total=len(out))

@router.get("/{dish_id}", response_model=DishDetailOut)
async def dish_detail(dish_id: int, db: AsyncSession = Depends(get_db)):
    dish, specs = await get_dish_detail(db, dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="dish_not_found")
    return DishDetailOut(
        id=int(dish.id),
        category_id=int(dish.category_id) if dish.category_id is not None else None,
        name=dish.name,
        description=dish.description,
        price=float(dish.price),
        image_url=dish.image_url,
        status=dish.status,
        rating_avg=float(dish.rating_avg),
        rating_count=int(dish.rating_count),
        sales_count=int(dish.sales_count),
        ai_metadata=dish.ai_metadata or {},
        specs=[DishSpecOut(id=int(s.id), spec_name=s.spec_name, spec_values=s.spec_values or []) for s in specs]
    )

@router.get("/recommend/home", response_model=DishListOut)
async def home_recommend(user: User = Depends(require_user), db: AsyncSession = Depends(get_db)):
    # 固定决策：使用用户 tags 做轻量个性化
    # tags 从 preferences 读在 users/preferences 接口，前端也可缓存；这里不再 join，保持接口快
    # 一期：直接热销/高评分推荐，个性化在前端更精细也可；这里提供基础版
    dishes = await recommend_home(db, user_tags=[])
    out = []
    for d in dishes:
        out.append(DishListItem(
            id=int(d.id),
            name=d.name,
            price=float(d.price),
            image_url=d.image_url,
            status=d.status,
            rating_avg=float(d.rating_avg),
            rating_count=int(d.rating_count),
            sales_count=int(d.sales_count),
            ai_highlights=compute_highlights(d.ai_metadata or {})
        ))
    return DishListOut(items=out, total=len(out))
