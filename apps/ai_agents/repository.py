"""repository module."""

import logging

logger = logging.getLogger(__name__)

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apps.ai_agents.models import Conversation, Message
from apps.shared_core.database.repository import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    """Repository برای مدیریت مکالمات."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Conversation)
        """Handle __init__ (session)."""

    async def get_user_conversations(
        self, user_id: int, agent_type: str | None = None, limit: int = 50, offset: int = 0
    ) -> list[Conversation]:
        """دریافت مکالمات یک کاربر با تعداد پیام‌ها."""
        stmt = select(Conversation).where(Conversation.user_id == user_id)

        if agent_type:
            stmt = stmt.where(Conversation.agent_type == agent_type)

        stmt = stmt.order_by(Conversation.updated_at.desc()).limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_with_messages(self, conversation_id: int) -> Conversation | None:
        """دریافت مکالمه با تمام پیام‌ها."""
        stmt = (
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.id == conversation_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_message_count(self, conversation_id: int) -> int:
        """شمارش پیام‌های یک مکالمه."""
        stmt = (
            select(func.count())
            .select_from(Message)
            .where(Message.conversation_id == conversation_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()


class MessageRepository(BaseRepository[Message]):
    """Repository برای مدیریت پیام‌ها."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Message)
        """Handle __init__ (session)."""

    async def get_conversation_messages(
        self, conversation_id: int, limit: int = 100
    ) -> list[Message]:
        """دریافت پیام‌های یک مکالمه به ترتیب زمانی."""
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        tool_calls: dict | None = None,
        tool_call_id: str | None = None,
        metadata_json: dict | None = None,
    ) -> Message:
        """ایجاد پیام جدید."""
        data = {
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "tool_calls": tool_calls,
            "tool_call_id": tool_call_id,
            "metadata_json": metadata_json or {},
        }
        return await self.create(data)
