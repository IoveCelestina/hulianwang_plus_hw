from sqlalchemy import BigInteger, Integer, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Cart(Base):
    __tablename__ = "carts"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    updated_at: Mapped[str | None] = mapped_column(TIMESTAMP)

class CartItem(Base):
    __tablename__ = "cart_items"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    cart_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    dish_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    selected_specs: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[str | None] = mapped_column(TIMESTAMP)
