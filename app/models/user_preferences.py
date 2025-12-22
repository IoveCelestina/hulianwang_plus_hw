from sqlalchemy import BigInteger, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class UserPreferences(Base):
    __tablename__ = "user_preferences"
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    explicit_tags: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    implicit_profile: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    dietary_restrictions: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    last_updated: Mapped[str | None] = mapped_column(TIMESTAMP)
