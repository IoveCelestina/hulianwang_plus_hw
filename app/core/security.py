from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any

from jose import jwt
from passlib.context import CryptContext


# 固定决策：使用 PBKDF2-SHA256，避免 bcrypt 在部分环境的兼容问题
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
)

JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret_change_me")
JWT_ALG = "HS256"
JWT_EXPIRE_MIN = int(os.getenv("JWT_EXPIRE_MIN", "10080"))  # 默认 7 天


def hash_password(raw: str) -> str:
    # 固定决策：限制密码长度，避免极端输入导致计算异常或DoS
    if raw is None:
        raise ValueError("password_required")
    raw = str(raw)
    if len(raw) < 6:
        raise ValueError("password_too_short")
    if len(raw) > 128:
        raise ValueError("password_too_long")
    return pwd_context.hash(raw)


def verify_password(raw: str, hashed: str) -> bool:
    if not raw or not hashed:
        return False
    raw = str(raw)
    if len(raw) > 128:
        return False
    return pwd_context.verify(raw, hashed)


def create_access_token(user_id: int) -> str:
    now = datetime.utcnow()
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=JWT_EXPIRE_MIN)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
