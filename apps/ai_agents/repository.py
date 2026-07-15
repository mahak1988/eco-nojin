from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from apps.shared_core.database.repository import BaseRepository
from apps.ai_agents.models import Conversation, Message

class ConversationRepository(BaseRepository[Conversation]):
    """Repository برای مدیریت مکالمات."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Conversation)
    
    async def get_user_conversations(
        self,
        user_id: int,
        agent_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Conversation]:
        """دریافت مکالمات یک کاربر با تعداد پیام‌ها."""
        stmt = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
        )
        
        if agent_type:
            stmt = stmt.where(Conversation.agent_type == agent_type)
        
        stmt = (
            stmt
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_with_messages(self, conversation_id: int) -> Optional[Conversation]:
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
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Message)
    
    async def get_conversation_messages(
        self,
        conversation_id: int,
        limit: int = 100
    ) -> List[Message]:
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
        tool_calls: Optional[dict] = None,
        tool_call_id: Optional[str] = None,
        metadata_json: Optional[dict] = None
    ) -> Message:
        """ایجاد پیام جدید."""
        data = {
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "tool_calls": tool_calls,
            "tool_call_id": tool_call_id,
            "metadata_json": metadata_json or {}
        }
        return await self.create(data)