from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func
from typing import List, Optional, Dict, Any
import logging

from apps.shared_knowledge.knowledge.models import (
    KnowledgeArticle,
    BusinessRule,
    ResponseTemplate,
    AgentMemory
)

logger = logging.getLogger(__name__)


class KnowledgeRepository:
    """Repository برای مدیریت دانش‌نامه."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    # ==========================================
    # Knowledge Articles
    # ==========================================
    async def search_articles(
        self,
        agent_type: str,
        query: str,
        limit: int = 5
    ) -> List[KnowledgeArticle]:
        """جستجوی مقالات مرتبط با query."""
        # تبدیل query به keywords
        keywords = [k.strip().lower() for k in query.split() if len(k.strip()) > 2]
        
        stmt = select(KnowledgeArticle).where(
            and_(
                KnowledgeArticle.agent_type == agent_type,
                KnowledgeArticle.is_active == True
            )
        )
        
        # جستجو در title، content و keywords
        if keywords:
            conditions = []
            for keyword in keywords:
                conditions.append(
                    or_(
                        KnowledgeArticle.title.ilike(f"%{keyword}%"),
                        KnowledgeArticle.content.ilike(f"%{keyword}%"),
                        KnowledgeArticle.keywords.ilike(f"%{keyword}%")
                    )
                )
            stmt = stmt.where(or_(*conditions))
        
        stmt = stmt.order_by(
            KnowledgeArticle.priority.desc(),
            KnowledgeArticle.updated_at.desc()
        ).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_articles_by_category(
        self,
        agent_type: str,
        category: str
    ) -> List[KnowledgeArticle]:
        """دریافت مقالات بر اساس دسته‌بندی."""
        stmt = select(KnowledgeArticle).where(
            and_(
                KnowledgeArticle.agent_type == agent_type,
                KnowledgeArticle.category == category,
                KnowledgeArticle.is_active == True
            )
        ).order_by(KnowledgeArticle.priority.desc())
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def create_article(self, data: Dict[str, Any]) -> KnowledgeArticle:
        """ایجاد مقاله جدید."""
        article = KnowledgeArticle(**data)
        self.session.add(article)
        await self.session.flush()
        await self.session.refresh(article)
        return article
    
    # ==========================================
    # Business Rules
    # ==========================================
    async def get_active_rules(self, agent_type: str) -> List[BusinessRule]:
        """دریافت قوانین فعال برای یک ایجنت."""
        stmt = select(BusinessRule).where(
            and_(
                BusinessRule.agent_type == agent_type,
                BusinessRule.is_active == True
            )
        ).order_by(BusinessRule.priority.desc())
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def create_rule(self, data: Dict[str, Any]) -> BusinessRule:
        """ایجاد قانون جدید."""
        rule = BusinessRule(**data)
        self.session.add(rule)
        await self.session.flush()
        await self.session.refresh(rule)
        return rule
    
    # ==========================================
    # Response Templates
    # ==========================================
    async def get_template(
        self,
        agent_type: str,
        intent: str
    ) -> Optional[ResponseTemplate]:
        """دریافت قالب پاسخ برای یک intent."""
        stmt = select(ResponseTemplate).where(
            and_(
                ResponseTemplate.agent_type == agent_type,
                ResponseTemplate.intent == intent,
                ResponseTemplate.is_active == True
            )
        )
        
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def create_template(self, data: Dict[str, Any]) -> ResponseTemplate:
        """ایجاد قالب جدید."""
        template = ResponseTemplate(**data)
        self.session.add(template)
        await self.session.flush()
        await self.session.refresh(template)
        return template
    
    # ==========================================
    # Agent Memory
    # ==========================================
    async def save_memory(
        self,
        agent_type: str,
        user_id: int,
        memory_type: str,
        content: str,
        importance: float = 0.5
    ) -> AgentMemory:
        """ذخیره حافظه ایجنت."""
        memory = AgentMemory(
            agent_type=agent_type,
            user_id=user_id,
            memory_type=memory_type,
            content=content,
            importance=importance
        )
        self.session.add(memory)
        await self.session.flush()
        await self.session.refresh(memory)
        return memory
    
    async def get_user_memories(
        self,
        agent_type: str,
        user_id: int,
        limit: int = 10
    ) -> List[AgentMemory]:
        """دریافت حافظه‌های کاربر برای یک ایجنت."""
        stmt = select(AgentMemory).where(
            and_(
                AgentMemory.agent_type == agent_type,
                AgentMemory.user_id == user_id
            )
        ).order_by(
            AgentMemory.importance.desc(),
            AgentMemory.last_accessed.desc()
        ).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def update_memory_access(self, memory_id: int):
        """بروزرسانی زمان دسترسی به حافظه."""
        stmt = select(AgentMemory).where(AgentMemory.id == memory_id)
        result = await self.session.execute(stmt)
        memory = result.scalars().first()
        
        if memory:
            memory.last_accessed = func.now()
            await self.session.flush()