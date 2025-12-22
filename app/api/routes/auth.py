from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.auth import RegisterIn, LoginIn, TokenOut

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=TokenOut)
async def register(data: RegisterIn, db: AsyncSession = Depends(get_db)):
    exist = await db.execute(select(User).where(User.username == data.username))
    if exist.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="username_taken")

    u = User(username=data.username, password_hash=hash_password(data.password), phone=data.phone, role="user")
    db.add(u)
    await db.commit()
    await db.refresh(u)

    token = create_access_token(int(u.id))
    return TokenOut(user_id=int(u.id), access_token=token)


@router.post("/login", response_model=TokenOut)
async def login(data: LoginIn, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User).where(User.username == data.username))
    u = res.scalar_one_or_none()
    if not u or not verify_password(data.password, u.password_hash):
        raise HTTPException(status_code=401, detail="invalid_credentials")

    token = create_access_token(int(u.id))
    return TokenOut(user_id=int(u.id), access_token=token)
