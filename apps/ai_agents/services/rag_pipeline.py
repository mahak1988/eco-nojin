"""
RAG (Retrieval-Augmented Generation) Pipeline for Econojin AI Agents.

This module provides context-aware responses by retrieving relevant
information from the knowledge base before generating answers.
"""

from typing import List, Dict, Any, Optional
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
import json

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    خط لوله RAG برای بازیابی اطلاعات مرتبط از پایگاه دانش.
    
    قابلیت‌ها:
    - جستجو در مستندات پروژه
    - بازیابی کدهای مرتبط
    - استخراج اطلاعات از دیتابیس
    - ترکیب context برای LLM
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def search_documents(
        self,
        query: str,
        limit: int = 5,
        categories: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        جستجو در مستندات پروژه.
        
        Args:
            query: متن جستجو
            limit: حداکثر تعداد نتایج
            categories: فیلتر دسته‌بندی‌ها
        
        Returns:
            لیست مستندات مرتبط
        """
        try:
            # جستجوی ساده در جدول library_resources
            from apps.library.models import LibraryResource
            
            stmt = select(LibraryResource).where(
                LibraryResource.title.ilike(f"%{query}%")
            ).limit(limit)
            
            if categories:
                stmt = stmt.where(LibraryResource.category.in_(categories))
            
            result = await self.session.execute(stmt)
            resources = result.scalars().all()
            
            return [
                {
                    "type": "document",
                    "title": r.title,
                    "description": r.description,
                    "url": r.file_url if hasattr(r, 'file_url') else None,
                    "category": r.category if hasattr(r, 'category') else "general"
                }
                for r in resources
            ]
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    async def search_code_examples(
        self,
        query: str,
        language: Optional[str] = None,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        جستجو در مثال‌های کد.
        
        Args:
            query: متن جستجو
            language: فیلتر زبان برنامه‌نویسی
            limit: حداکثر تعداد نتایج
        
        Returns:
            لیست مثال‌های کد مرتبط
        """
        # این تابع می‌تواند بعداً به یک vector DB متصل شود
        # فعلاً به صورت hardcoded مثال برمی‌گرداند
        code_examples = {
            "fastapi": {
                "title": "FastAPI Endpoint Example",
                "language": "python",
                "code": """
@router.get("/items/{item_id}")
async def get_item(item_id: int):
    return {"item_id": item_id}
"""
            },
            "sqlalchemy": {
                "title": "SQLAlchemy Query Example",
                "language": "python",
                "code": """
result = await session.execute(
    select(User).where(User.id == user_id)
)
user = result.scalar_one_or_none()
"""
            },
            "react": {
                "title": "React Component Example",
                "language": "typescript",
                "code": """
function MyComponent({ data }) {
  return <div>{data.title}</div>;
}
"""
            }
        }
        
        results = []
        for key, example in code_examples.items():
            if query.lower() in key or query.lower() in example["title"].lower():
                if language is None or example["language"] == language:
                    results.append(example)
                    if len(results) >= limit:
                        break
        
        return results
    
    async def get_database_context(
        self,
        table_name: str,
        sample_size: int = 5
    ) -> Dict[str, Any]:
        """
        دریافت نمونه‌ای از داده‌های یک جدول.
        
        Args:
            table_name: نام جدول
            sample_size: تعداد رکوردهای نمونه
        
        Returns:
            اطلاعات جدول و نمونه داده‌ها
        """
        try:
            # بررسی وجود جدول
            from sqlalchemy import inspect
            
            inspector = await self.session.sync_session.run_sync(inspect)
            table_names = inspector.get_table_names()
            
            if table_name not in table_names:
                return {"error": f"Table {table_name} not found"}
            
            # دریافت schema
            columns = inspector.get_columns(table_name)
            column_info = [
                {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"]
                }
                for col in columns
            ]
            
            # دریافت نمونه داده‌ها
            query = text(f"SELECT * FROM {table_name} LIMIT :limit")
            result = await self.session.execute(query, {"limit": sample_size})
            rows = result.fetchall()
            
            return {
                "table_name": table_name,
                "columns": column_info,
                "sample_data": [dict(row._mapping) for row in rows],
                "row_count": len(rows)
            }
        except Exception as e:
            logger.error(f"Error getting database context: {e}")
            return {"error": str(e)}
    
    async def build_context(
        self,
        query: str,
        agent_type: str,
        include_documents: bool = True,
        include_code: bool = True,
        include_db: bool = False
    ) -> str:
        """
        ساخت context کامل برای LLM.
        
        Args:
            query: پرسش کاربر
            agent_type: نوع ایجنت
            include_documents: شامل مستندات باشد
            include_code: شامل مثال‌های کد باشد
            include_db: شامل داده‌های دیتابیس باشد
        
        Returns:
            رشته context فرمت‌شده
        """
        context_parts = []
        
        # بخش مستندات
        if include_documents:
            docs = await self.search_documents(query, limit=3)
            if docs:
                context_parts.append("## مستندات مرتبط:\n")
                for doc in docs:
                    context_parts.append(f"- **{doc['title']}**: {doc['description']}\n")
        
        # بخش کد
        if include_code:
            keywords = self._extract_keywords(query)
            for keyword in keywords[:2]:
                code_examples = await self.search_code_examples(keyword, limit=1)
                if code_examples:
                    context_parts.append(f"\n## مثال کد ({keyword}):\n")
                    for ex in code_examples:
                        context_parts.append(f"```{ex['language']}\n{ex['code']}\n```\n")
        
        # بخش دیتابیس
        if include_db and agent_type in ["financial", "data_analyst"]:
            tables_to_check = ["users", "farms", "crops", "transactions"]
            for table in tables_to_check[:2]:
                db_context = await self.get_database_context(table, sample_size=2)
                if "error" not in db_context:
                    context_parts.append(f"\n## ساختار جدول {table}:\n")
                    context_parts.append(f"Columns: {[c['name'] for c in db_context['columns']]}\n")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def _extract_keywords(self, query: str) -> List[str]:
        """استخراج کلمات کلیدی از پرسش."""
        # حذف کلمات رایج فارسی و انگلیسی
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "در", "به", "از", "که", "را", "با", "برای", "یک", "این", "آن"
        }
        
        words = query.split()
        keywords = [
            word.strip(".,!?()[]{}\"'").lower()
            for word in words
            if word.lower() not in stop_words and len(word) > 2
        ]
        
        return keywords[:5]  # حداکثر ۵ کلمه کلیدی
    
    async def enhance_prompt(
        self,
        original_prompt: str,
        agent_type: str,
        context: Optional[str] = None
    ) -> str:
        """
        تقویت prompt با context اضافی.
        
        Args:
            original_prompt: prompt اصلی کاربر
            agent_type: نوع ایجنت
            context: context از قبل محاسبه شده
        
        Returns:
            prompt تقویت شده
        """
        if context is None:
            context = await self.build_context(original_prompt, agent_type)
        
        if not context:
            return original_prompt
        
        enhanced = f"""
<context>
{context}
</context>

<instruction>
با توجه به اطلاعات بالا، به سوال زیر پاسخ دهید:
</instruction>

<question>
{original_prompt}
</question>
"""
        return enhanced
