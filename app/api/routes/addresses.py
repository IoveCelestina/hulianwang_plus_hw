from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.db.session import get_db
from app.core.deps import require_user
from app.models.user import User
from app.models.address import UserAddress
from app.schemas.user import AddressIn, AddressOut

router = APIRouter(prefix="/addresses")


@router.get("", response_model=list[AddressOut])
async def list_addresses(user: User = Depends(require_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(UserAddress)
        .where(UserAddress.user_id == int(user.id))
        .order_by(UserAddress.created_at.desc())
    )
    items = []
    for a in res.scalars().all():
        items.append(
            AddressOut(
                id=int(a.id),
                contact_name=a.contact_name,
                phone=a.phone,
                address_line=a.address_line,
                is_default=bool(a.is_default),
            )
        )
    return items


@router.post("", response_model=AddressOut)
async def create_address(data: AddressIn, user: User = Depends(require_user), db: AsyncSession = Depends(get_db)):
    if data.is_default:
        await db.execute(
            update(UserAddress)
            .where(UserAddress.user_id == int(user.id))
            .values(is_default=False)
        )

    a = UserAddress(
        user_id=int(user.id),
        contact_name=data.contact_name,
        phone=data.phone,
        address_line=data.address_line,
        is_default=bool(data.is_default),
    )
    db.add(a)
    await db.commit()
    await db.refresh(a)
    return AddressOut(
        id=int(a.id),
        contact_name=a.contact_name,
        phone=a.phone,
        address_line=a.address_line,
        is_default=bool(a.is_default),
    )


@router.post("/{address_id}/set-default")
async def set_default(address_id: int, user: User = Depends(require_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(UserAddress).where(UserAddress.id == address_id, UserAddress.user_id == int(user.id))
    )
    a = res.scalar_one_or_none()
    if not a:
        raise HTTPException(status_code=404, detail="address_not_found")

    await db.execute(
        update(UserAddress)
        .where(UserAddress.user_id == int(user.id))
        .values(is_default=False)
    )
    a.is_default = True
    db.add(a)
    await db.commit()
    return {"ok": True}
