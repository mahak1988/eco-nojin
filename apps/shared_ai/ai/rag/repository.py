from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional, Dict, Any
import logging

from apps.shared_ai.ai.rag.models import Document, DocumentChunk

logger = logging.getLogger(__name__)


class RAGRepository:
    """Repository برای مدیریت اسناد RAG."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_document(self, data: Dict[str, Any]) -> Document:
        """ایجاد سند جدید."""
        doc = Document(**data)
        self.session.add(doc)
        await self.session.flush()
        await self.session.refresh(doc)
        return doc
    
    async def get_document(self, document_id: int, user_id: int) -> Optional[Document]:
        """دریافت سند با بررسی مالکیت."""
        stmt = select(Document).where(
            Document.id == document_id,
            Document.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def get_user_documents(self, user_id: int, limit: int = 50) -> List[Document]:
        """دریافت لیست اسناد کاربر."""
        stmt = select(Document).where(
            Document.user_id == user_id
        ).order_by(Document.created_at.desc()).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def create_chunk(self, data: Dict[str, Any]) -> DocumentChunk:
        """ایجاد chunk جدید."""
        chunk = DocumentChunk(**data)
        self.session.add(chunk)
        await self.session.flush()
        await self.session.refresh(chunk)
        return chunk
    
    async def get_document_chunks(self, document_id: int) -> List[DocumentChunk]:
        """دریافت تمام chunks یک سند."""
        stmt = select(DocumentChunk).where(
            DocumentChunk.document_id == document_id
        ).order_by(DocumentChunk.chunk_index)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def delete_document(self, document_id: int, user_id: int) -> bool:
        """حذف سند و chunks آن."""
        # بررسی مالکیت
        doc = await self.get_document(document_id, user_id)
        if not doc:
            return False
        
        # حذف chunks
        stmt = delete(DocumentChunk).where(DocumentChunk.document_id == document_id)
        await self.session.execute(stmt)
        
        # حذف سند
        stmt = delete(Document).where(Document.id == document_id)
        await self.session.execute(stmt)
        
        await self.session.flush()
        return True
    
    async def update_document_processed(
        self,
        document_id: int,
        chunk_count: int
    ) -> bool:
        """بروزرسانی وضعیت پردازش سند."""
        stmt = select(Document).where(Document.id == document_id)
        result = await self.session.execute(stmt)
        doc = result.scalars().first()
        
        if doc:
            doc.is_processed = True
            doc.chunk_count = chunk_count
            await self.session.flush()
            return True
        
        return False