from sqlalchemy import BigInteger, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    summary: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[object | None] = mapped_column(TIMESTAMP)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    session_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user / assistant
    content: Mapped[str] = mapped_column(Text, nullable=False)

    recommended_dish_ids: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    candidate_dish_ids: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    created_at: Mapped[object | None] = mapped_column(TIMESTAMP)
