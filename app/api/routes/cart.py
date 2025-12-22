from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.deps import require_user
from app.models.user import User
from app.schemas.cart import CartOut, CartItemIn, CartItemUpdateIn
from app.services.cart_service import get_cart_view, add_to_cart, update_cart_item, delete_cart_item

router = APIRouter(prefix="/cart")

@router.get("", response_model=CartOut)
async def get_cart(user: User = Depends(require_user), db: AsyncSession = Depends(get_db)):
    items, total = await get_cart_view(db, int(user.id))
    return CartOut(items=items, total_amount=total)

@router.post("/items")
async def add_item(payload: CartItemIn, user: User = Depends(require_user), db: AsyncSession = Depends(get_db)):
    try:
        await add_to_cart(db, int(user.id), payload.dish_id, payload.quantity, payload.selected_specs)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True}

@router.put("/items/{item_id}")
async def update_item(item_id: int, payload: CartItemUpdateIn, user: User = Depends(require_user), db: AsyncSession = Depends(get_db)):
    try:
        await update_cart_item(db, int(user.id), item_id, payload.quantity, payload.selected_specs)
    except ValueError as e:
        raise HTTPException(status_code=404 if "not_found" in str(e) else 400, detail=str(e))
    return {"ok": True}

@router.delete("/items/{item_id}")
async def delete_item(item_id: int, user: User = Depends(require_user), db: AsyncSession = Depends(get_db)):
    try:
        await delete_cart_item(db, int(user.id), item_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"ok": True}
