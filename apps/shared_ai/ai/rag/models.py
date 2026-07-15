from sqlalchemy import String, Text, Integer, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from apps.shared_core.database.session import Base


class Document(Base):
    """سند آپلود شده توسط کاربر."""
    __tablename__ = "rag_documents"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)  # pdf, txt, md
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    
    # متادیتا
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        onupdate="now()",
        nullable=False
    )


class DocumentChunk(Base):
    """تکه‌های سند برای جستجوی برداری."""
    __tablename__ = "rag_document_chunks"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("rag_documents.id", ondelete="CASCADE"), index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # متادیتا
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Qdrant point ID
    qdrant_id: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        nullable=False
    )