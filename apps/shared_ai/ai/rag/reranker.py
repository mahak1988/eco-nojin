"""
Reranker با Cross-Encoder برای بهبود دقت نتایج
"""

from typing import List, Dict, Any
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


class CrossEncoderReranker:
    """Reranker با استفاده از Cross-Encoder."""
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self._model = None
    
    @property
    def model(self):
        """Lazy loading مدل."""
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder
                logger.info(f"🎯 Loading reranker model: {self.model_name}")
                self._model = CrossEncoder(self.model_name)
                logger.info(f"✅ Reranker model loaded")
            except ImportError:
                logger.error("❌ sentence-transformers not installed")
                raise RuntimeError("sentence-transformers not installed")
        
        return self._model
    
    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        مرتب‌سازی مجدد نتایج با Cross-Encoder.
        
        Args:
            query: عبارت جستجو
            documents: لیست نتایج اولیه
            top_k: تعداد نتایج نهایی
        
        Returns:
            لیست نتایج مرتب‌شده بر اساس relevance
        """
        if not documents:
            return []
        
        logger.info(f"🎯 Reranking {len(documents)} documents...")
        
        # ساخت pairs برای Cross-Encoder
        pairs = [[query, doc["text"]] for doc in documents]
        
        # محاسبه امتیازها
        scores = self.model.predict(pairs)
        
        # افزودن امتیاز به نتایج
        for i, doc in enumerate(documents):
            doc["rerank_score"] = float(scores[i])
        
        # مرتب‌سازی بر اساس rerank_score
        documents.sort(key=lambda x: x["rerank_score"], reverse=True)
        
        # بازگشت top_k
        reranked = documents[:top_k]
        
        logger.info(f"✅ Reranking completed: top score = {reranked[0]['rerank_score']:.4f}")
        
        return reranked


# Singleton instance
@lru_cache()
def get_reranker() -> CrossEncoderReranker:
    """دریافت نمونه singleton از reranker."""
    return CrossEncoderReranker()