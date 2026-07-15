from typing import List
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """مدل embedding برای تبدیل متن به بردار."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        self._dimension = 384  # all-MiniLM-L6-v2
    
    @property
    def model(self):
        """Lazy loading مدل."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"🧠 Loading embedding model: {self.model_name}")
                self._model = SentenceTransformer(self.model_name)
                logger.info(f"✅ Embedding model loaded (dimension: {self._dimension})")
            except ImportError:
                logger.error("❌ sentence-transformers not installed")
                raise RuntimeError("sentence-transformers not installed. Run: pip install sentence-transformers")
        
        return self._model
    
    @property
    def dimension(self) -> int:
        """بعد بردار embedding."""
        return self._dimension
    
    def embed_text(self, text: str) -> List[float]:
        """تبدیل متن به بردار embedding."""
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """تبدیل چند متن به بردارهای embedding."""
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return [emb.tolist() for emb in embeddings]
    
    def similarity(self, text1: str, text2: str) -> float:
        """محاسبه شباهت بین دو متن."""
        emb1 = self.embed_text(text1)
        emb2 = self.embed_text(text2)
        
        # Cosine similarity
        dot_product = sum(a * b for a, b in zip(emb1, emb2))
        return dot_product


# Singleton instance
@lru_cache()
def get_embedding_model() -> EmbeddingModel:
    """دریافت نمونه singleton از embedding model."""
    return EmbeddingModel()