from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.db.session import get_db
from app.core.deps import require_admin
from app.models.user import User
from app.models.dish import Dish, Category
from app.models.order import Order
from app.models.review import Review

router = APIRouter(prefix="/admin")

@router.get("/categories")
async def admin_categories(admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Category).order_by(Category.sort_order.asc(), Category.id.asc()))
    return [{"id": int(c.id), "name": c.name, "sort_order": int(c.sort_order or 0)} for c in res.scalars().all()]

@router.post("/categories")
async def admin_create_category(payload: dict, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    name = str(payload.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="name_required")
    c = Category(name=name, sort_order=int(payload.get("sort_order") or 0))
    db.add(c)
    await db.commit()
    await db.refresh(c)
    return {"id": int(c.id)}

@router.get("/dishes")
async def admin_list_dishes(admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Dish).order_by(Dish.id.desc()).limit(200))
    out = []
    for d in res.scalars().all():
        out.append({
            "id": int(d.id),
            "name": d.name,
            "price": float(d.price),
            "status": d.status,
            "category_id": d.category_id,
            "ai_metadata": d.ai_metadata or {}
        })
    return out

@router.post("/dishes")
async def admin_create_dish(payload: dict, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    d = Dish(
        category_id=payload.get("category_id"),
        name=str(payload.get("name") or "").strip(),
        description=payload.get("description"),
        price=float(payload.get("price") or 0),
        image_url=payload.get("image_url"),
        status=payload.get("status") or "on_sale",
        ai_metadata=payload.get("ai_metadata") or {}
    )
    if not d.name or d.price <= 0:
        raise HTTPException(status_code=400, detail="invalid_dish")
    db.add(d)
    await db.commit()
    await db.refresh(d)
    return {"id": int(d.id)}

@router.put("/dishes/{dish_id}")
async def admin_update_dish(dish_id: int, payload: dict, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Dish).where(Dish.id == dish_id))
    d = res.scalar_one_or_none()
    if not d:
        raise HTTPException(status_code=404, detail="dish_not_found")

    for k in ["name","description","image_url","status"]:
        if k in payload:
            setattr(d, k, payload[k])
    if "price" in payload:
        d.price = float(payload["price"])
    if "category_id" in payload:
        d.category_id = payload["category_id"]
    if "ai_metadata" in payload:
        d.ai_metadata = payload["ai_metadata"] or {}

    db.add(d)
    await db.commit()
    return {"ok": True}

@router.get("/orders")
async def admin_orders(admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Order).order_by(Order.created_at.desc()).limit(200))
    return [{
        "id": int(o.id),
        "user_id": int(o.user_id),
        "status": o.status,
        "total_amount": float(o.total_amount),
        "created_at": str(o.created_at) if o.created_at else None
    } for o in res.scalars().all()]

@router.put("/orders/{order_id}/status")
async def admin_set_order_status(order_id: int, payload: dict, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    new_status = str(payload.get("status") or "").strip()
    if new_status not in {"pending","paid","completed","cancelled"}:
        raise HTTPException(status_code=400, detail="invalid_status")
    res = await db.execute(select(Order).where(Order.id == order_id))
    o = res.scalar_one_or_none()
    if not o:
        raise HTTPException(status_code=404, detail="order_not_found")
    o.status = new_status
    db.add(o)
    await db.commit()
    return {"ok": True}

@router.get("/reviews")
async def admin_reviews(admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Review).order_by(Review.created_at.desc()).limit(200))
    return [{
        "id": int(r.id),
        "user_id": int(r.user_id),
        "dish_id": int(r.dish_id),
        "order_id": int(r.order_id),
        "rating": int(r.rating),
        "comment": r.comment,
        "tags": r.tags or [],
        "created_at": str(r.created_at) if r.created_at else None
    } for r in res.scalars().all()]
