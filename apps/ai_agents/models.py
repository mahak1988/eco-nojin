"""models module."""

import logging

logger = logging.getLogger(__name__)
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.shared_core.database.session import Base


class Conversation(Base):
    """
    مکالمه بین کاربر و ایجنت.
    هر مکالمه می‌تواند چندین پیام داشته باشد.
    """

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "financial", "support"
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # متادیتا
    metadata_json: Mapped[dict | None] = mapped_column(JSON, default=dict)

    # timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # relationships
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at"
    )


class Message(Base):
    """
    پیام در یک مکالمه.
    می‌تواند از طرف کاربر (human) یا ایجنت (ai) باشد.
    """

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conversations.id", ondelete="CASCADE"), index=True
    )

    role: Mapped[str] = mapped_column(String(20), nullable=False)  # "user", "assistant", "tool"
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # برای tool calls
    tool_calls: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    tool_call_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # متادیتا (مثل tokens, latency)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    metadata_json: Mapped[dict | None] = mapped_column(JSON, default=dict)
    # relationships
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
