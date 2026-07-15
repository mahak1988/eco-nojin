from sqlalchemy import String, Text, Integer, Boolean, DateTime, Float, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List, Optional
from apps.shared_core.database.session import Base


class KnowledgeArticle(Base):
    """مقاله دانش‌نامه برای هر ایجنت."""
    __tablename__ = "knowledge_articles"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    agent_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    keywords: Mapped[str] = mapped_column(Text, nullable=False)  # comma-separated
    priority: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<KnowledgeArticle(agent={self.agent_type}, title='{self.title}')>"


class BusinessRule(Base):
    """قوانین کسب‌وکار برای ایجنت‌ها."""
    __tablename__ = "business_rules"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    agent_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    rule_name: Mapped[str] = mapped_column(String(100), nullable=False)
    condition: Mapped[str] = mapped_column(Text, nullable=False)  # JSON condition
    action: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )


class ResponseTemplate(Base):
    """قالب‌های پاسخ برای ایجنت‌ها."""
    __tablename__ = "response_templates"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    agent_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    intent: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    template: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class AgentMemory(Base):
    """حافظه ایجنت‌ها از مکالمات قبلی."""
    __tablename__ = "agent_memories"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    agent_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    memory_type: Mapped[str] = mapped_column(String(50), nullable=False)  # fact, preference, context
    content: Mapped[str] = mapped_column(Text, nullable=False)
    importance: Mapped[float] = mapped_column(Float, default=0.5)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    last_accessed: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

# ============================================================
# Compatibility Aliases (Added by Phase 2 Fix)
# ============================================================

KnowledgeItem = KnowledgeArticle
