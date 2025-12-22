from __future__ import annotations

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select

from app.models.user import User
from app.core.security import JWT_SECRET, JWT_ALG
from app.db.session import AsyncSessionLocal  # 关键：独立 session

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> User:
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="not_authenticated")

    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=401, detail="invalid_token")
        user_id = int(sub)
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="invalid_token")

    # 关键：鉴权查询用自己的 session，避免污染业务 session 的事务状态
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(User).where(User.id == user_id))
        user = res.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="user_not_found")
    return user


async def require_user(user: User = Depends(get_current_user)) -> User:
    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if getattr(user, "role", "user") != "admin":
        raise HTTPException(status_code=403, detail="forbidden")
    return user
