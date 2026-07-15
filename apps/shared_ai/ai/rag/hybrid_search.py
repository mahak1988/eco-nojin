"""
Hybrid Search: ترکیب BM25 (Keyword) + Vector (Semantic)
"""

from typing import List, Dict, Any, Optional, Tuple
import logging
import math
from collections import defaultdict
import re

logger = logging.getLogger(__name__)


class BM25:
    """پیاده‌سازی BM25 برای جستجوی keyword-based."""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus = []
        self.doc_lengths = []
        self.avgdl = 0
        self.idf = {}
        self.doc_freqs = defaultdict(int)
        self.n_docs = 0
    
    def _tokenize(self, text: str) -> List[str]:
        """توکنایز ساده متن."""
        # تبدیل به lowercase و حذف کاراکترهای خاص
        text = text.lower()
        text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text)  # حفظ کاراکترهای فارسی
        tokens = text.split()
        return [token for token in tokens if len(token) > 1]
    
    def fit(self, documents: List[str]):
        """آموزش BM25 روی corpus."""
        self.corpus = [self._tokenize(doc) for doc in documents]
        self.doc_lengths = [len(doc) for doc in self.corpus]
        self.n_docs = len(self.corpus)
        self.avgdl = sum(self.doc_lengths) / self.n_docs if self.n_docs > 0 else 0
        
        # محاسبه IDF
        for doc in self.corpus:
            unique_tokens = set(doc)
            for token in unique_tokens:
                self.doc_freqs[token] += 1
        
        for token, freq in self.doc_freqs.items():
            self.idf[token] = math.log((self.n_docs - freq + 0.5) / (freq + 0.5) + 1)
        
        logger.info(f"✅ BM25 fitted on {self.n_docs} documents")
    
    def score(self, query: str, doc_index: int) -> float:
        """محاسبه امتیاز BM25 برای یک سند."""
        if doc_index >= len(self.corpus):
            return 0.0
        
        query_tokens = self._tokenize(query)
        doc_tokens = self.corpus[doc_index]
        doc_len = self.doc_lengths[doc_index]
        
        score = 0.0
        token_freqs = defaultdict(int)
        
        for token in doc_tokens:
            token_freqs[token] += 1
        
        for token in query_tokens:
            if token in token_freqs:
                freq = token_freqs[token]
                idf = self.idf.get(token, 0)
                
                numerator = freq * (self.k1 + 1)
                denominator = freq + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)
                
                score += idf * numerator / denominator
        
        return score
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """جستجو و بازگشت top_k نتایج."""
        scores = []
        
        for i in range(self.n_docs):
            score = self.score(query, i)
            scores.append((i, score))
        
        # مرتب‌سازی بر اساس امتیاز
        scores.sort(key=lambda x: x[1], reverse=True)
        
        return scores[:top_k]


class HybridSearchEngine:
    """موتور جستجوی ترکیبی BM25 + Vector."""
    
    def __init__(self, vector_store, rrf_k: int = 60):
        self.vector_store = vector_store
        self.bm25 = BM25()
        self.rrf_k = rrf_k
        self.documents = []  # ذخیره متن‌ها برای BM25
        self.metadata_list = []  # ذخیره metadata
    
    def add_documents(self, texts: List[str], metadata_list: List[Dict[str, Any]]):
        """افزودن اسناد به هر دو سیستم."""
        # افزودن به vector store
        doc_ids = self.vector_store.add_documents(texts, metadata_list)
        
        # افزودن به BM25
        self.documents.extend(texts)
        self.metadata_list.extend(metadata_list)
        
        # بازآموزش BM25
        self.bm25.fit(self.documents)
        
        logger.info(f"✅ Added {len(texts)} documents to hybrid search")
        return doc_ids
    
    def reciprocal_rank_fusion(
        self,
        bm25_results: List[Tuple[int, float]],
        vector_results: List[Dict[str, Any]],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """ترکیب نتایج با Reciprocal Rank Fusion."""
        rrf_scores = defaultdict(float)
        
        # امتیازدهی BM25
        for rank, (doc_idx, _) in enumerate(bm25_results, 1):
            rrf_scores[doc_idx] += 1.0 / (self.rrf_k + rank)
        
        # امتیازدهی Vector
        for rank, result in enumerate(vector_results, 1):
            # پیدا کردن index سند در documents
            doc_text = result.get("text", "")
            for idx, doc in enumerate(self.documents):
                if doc == doc_text:
                    rrf_scores[idx] += 1.0 / (self.rrf_k + rank)
                    break
        
        # مرتب‌سازی بر اساس RRF score
        sorted_indices = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
        
        # ساخت نتایج نهایی
        results = []
        for idx in sorted_indices[:top_k]:
            if idx < len(self.documents):
                results.append({
                    "id": f"doc_{idx}",
                    "text": self.documents[idx],
                    "score": rrf_scores[idx],
                    "metadata": self.metadata_list[idx] if idx < len(self.metadata_list) else {},
                    "search_type": "hybrid"
                })
        
        return results
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        bm25_weight: float = 0.3,
        vector_weight: float = 0.7,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        جستجوی ترکیبی.
        
        Args:
            query: عبارت جستجو
            top_k: تعداد نتایج
            bm25_weight: وزن BM25 (پیش‌فرض: 0.3)
            vector_weight: وزن Vector (پیش‌فرض: 0.7)
            filter_metadata: فیلتر metadata
        
        Returns:
            لیست نتایج مرتب‌شده
        """
        logger.info(f"🔍 Hybrid search: {query[:50]}...")
        
        # جستجوی BM25
        bm25_top_k = top_k * 2  # بیشتر برای fusion
        bm25_results = self.bm25.search(query, top_k=bm25_top_k)
        
        # جستجوی Vector
        vector_top_k = top_k * 2
        vector_results = self.vector_store.search(
            query=query,
            top_k=vector_top_k,
            filter_metadata=filter_metadata
        )
        
        # Reciprocal Rank Fusion
        fused_results = self.reciprocal_rank_fusion(
            bm25_results=bm25_results,
            vector_results=vector_results,
            top_k=top_k
        )
        
        logger.info(f"✅ Hybrid search completed: {len(fused_results)} results")
        return fused_results


# Singleton instance
_hybrid_search_instance = None

def get_hybrid_search() -> HybridSearchEngine:
    """دریافت نمونه singleton از hybrid search."""
    global _hybrid_search_instance
    if _hybrid_search_instance is None:
        from apps.shared_ai.ai.rag.vector_store import get_vector_store
        vector_store = get_vector_store()
        _hybrid_search_instance = HybridSearchEngine(vector_store)
    return _hybrid_search_instance