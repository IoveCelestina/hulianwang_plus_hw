from sqlalchemy import String, BigInteger, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")
    created_at: Mapped[str | None] = mapped_column(TIMESTAMP)
    last_login_at: Mapped[str | None] = mapped_column(TIMESTAMP)
