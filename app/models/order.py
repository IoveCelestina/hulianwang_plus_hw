from sqlalchemy import BigInteger, Integer, String, DECIMAL, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    total_amount: Mapped[float] = mapped_column(DECIMAL(10,2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    context_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    address_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    note: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[str | None] = mapped_column(TIMESTAMP)

class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    order_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    dish_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    dish_name: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_snapshot: Mapped[float] = mapped_column(DECIMAL(10,2), nullable=False)
    selected_specs: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    ai_metadata_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
