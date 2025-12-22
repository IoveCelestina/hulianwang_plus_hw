from sqlalchemy import BigInteger, String, TIMESTAMP, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class UserAddress(Base):
    __tablename__ = "user_addresses"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    contact_name: Mapped[str] = mapped_column(String(50), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    address_line: Mapped[str] = mapped_column(String(255), nullable=False)

    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[object | None] = mapped_column(TIMESTAMP)
