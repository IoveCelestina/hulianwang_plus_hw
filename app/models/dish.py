from sqlalchemy import BigInteger, Integer, String, Text, DECIMAL, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

class Dish(Base):
    __tablename__ = "dishes"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    category_id: Mapped[int | None] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[float] = mapped_column(DECIMAL(10,2), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="on_sale")
    ai_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    sales_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rating_avg: Mapped[float] = mapped_column(DECIMAL(3,1), nullable=False, default=5.0)
    rating_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[str | None] = mapped_column(TIMESTAMP)
    updated_at: Mapped[str | None] = mapped_column(TIMESTAMP)

class DishSpec(Base):
    __tablename__ = "dish_specs"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    dish_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    spec_name: Mapped[str] = mapped_column(String(50), nullable=False)
    spec_values: Mapped[list] = mapped_column(JSONB, nullable=False)
