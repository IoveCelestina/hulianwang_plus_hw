from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.deps import require_user
from app.models.user import User
from app.schemas.review import ReviewCreateIn, ReviewOut, ReviewListOut
from app.services.review_service import create_review, list_reviews_by_dish

router = APIRouter(prefix="/reviews")


@router.post("", response_model=ReviewOut)
async def create(payload: ReviewCreateIn, user: User = Depends(require_user), db: AsyncSession = Depends(get_db)):
    try:
        rv = await create_review(
            db=db,
            user_id=int(user.id),
            order_id=payload.order_id,
            dish_id=payload.dish_id,
            rating=payload.rating,
            comment=payload.comment,
            tags=payload.tags,
        )
        return ReviewOut(
            id=int(rv.id),
            user_id=int(rv.user_id),
            dish_id=int(rv.dish_id),
            order_id=int(rv.order_id),
            rating=int(rv.rating),
            comment=rv.comment,
            tags=list(rv.tags or []),
            created_at=str(rv.created_at) if rv.created_at else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dish/{dish_id}", response_model=ReviewListOut)
async def list_by_dish(
    dish_id: int,
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_reviews_by_dish(db, dish_id, limit=limit, offset=offset)
    out = []
    for rv in items:
        out.append(
            ReviewOut(
                id=int(rv.id),
                user_id=int(rv.user_id),
                dish_id=int(rv.dish_id),
                order_id=int(rv.order_id),
                rating=int(rv.rating),
                comment=rv.comment,
                tags=list(rv.tags or []),
                created_at=str(rv.created_at) if rv.created_at else None,
            )
        )
    return ReviewListOut(items=out, total=total)
