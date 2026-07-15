from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import re

from apps.shared_knowledge.knowledge.repository import KnowledgeRepository
from apps.shared_knowledge.knowledge.models import KnowledgeArticle

logger = logging.getLogger(__name__)


class KnowledgeBaseEngine:
    """موتور جستجو و بازیابی دانش."""
    
    def __init__(self, session: AsyncSession):
        self.repo = KnowledgeRepository(session)
    
    async def search(
        self,
        agent_type: str,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """جستجوی دانش مرتبط."""
        logger.info(f"🔍 Searching knowledge for: {query[:50]}...")
        
        # جستجوی مقالات
        articles = await self.repo.search_articles(agent_type, query, limit)
        
        if not articles:
            # جستجو در تمام ایجنت‌ها
            articles = await self.repo.search_articles("all", query, limit)
        
        # امتیازدهی و مرتب‌سازی
        scored_articles = []
        for article in articles:
            score = self._calculate_relevance(article, query)
            scored_articles.append({
                "article": article,
                "score": score,
                "summary": self._generate_summary(article.content)
            })
        
        scored_articles.sort(key=lambda x: x["score"], reverse=True)
        
        logger.info(f"✅ Found {len(scored_articles)} relevant articles")
        return scored_articles[:limit]
    
    def _calculate_relevance(self, article: KnowledgeArticle, query: str) -> float:
        """محاسبه امتیاز مرتبط بودن."""
        score = 0.0
        
        # تبدیل به lowercase
        query_lower = query.lower()
        title_lower = article.title.lower()
        content_lower = article.content.lower()
        keywords_lower = article.keywords.lower()
        
        # امتیاز بر اساس موقعیت
        if query_lower in title_lower:
            score += 10.0
        
        if query_lower in keywords_lower:
            score += 8.0
        
        # امتیاز بر اساس تعداد تکرار
        query_words = query_lower.split()
        for word in query_words:
            if len(word) > 2:
                score += title_lower.count(word) * 2
                score += keywords_lower.count(word) * 1.5
                score += content_lower.count(word) * 0.5
        
        # امتیاز priority
        score += article.priority * 0.5
        
        return score
    
    def _generate_summary(self, content: str, max_length: int = 200) -> str:
        """تولید خلاصه از محتوا."""
        # حذف whitespace اضافی
        content = re.sub(r'\s+', ' ', content).strip()
        
        if len(content) <= max_length:
            return content
        
        # برش در مرز جمله
        truncated = content[:max_length]
        last_period = truncated.rfind('.')
        
        if last_period > max_length * 0.7:
            return truncated[:last_period + 1]
        
        return truncated + "..."
    
    async def get_context_for_agent(
        self,
        agent_type: str,
        query: str,
        max_tokens: int = 2000
    ) -> str:
        """دریافت context برای ایجنت."""
        articles = await self.search(agent_type, query, limit=3)
        
        if not articles:
            return ""
        
        context_parts = []
        total_length = 0
        
        for item in articles:
            article = item["article"]
            content = f"## {article.title}\n\n{article.content}\n\n"
            
            if total_length + len(content) > max_tokens:
                break
            
            context_parts.append(content)
            total_length += len(content)
        
        return "\n---\n\n".join(context_parts)