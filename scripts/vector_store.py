# agents/memory/vector_store.py
"""
مدیریت حافظه برداری با Qdrant
"""
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import structlog
import uuid

logger = structlog.get_logger()


class VectorMemory:
    """حافظه برداری برای RAG"""
    
    def __init__(self, collection_name: str = "econojin_memory"):
        self.collection_name = collection_name
        self.client = QdrantClient(host="localhost", port=6333)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.logger = logger.bind(component="vector_memory")
        
        self._ensure_collection()
    
    def _ensure_collection(self):
        """ایجاد collection اگر وجود ندارد"""
        collections = [c.name for c in self.client.get_collections().collections]
        
        if self.collection_name not in collections:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
            self.logger.info("collection_created", name=self.collection_name)
    
    def store(self, text: str, metadata: Dict[str, Any] = None):
        """ذخیره متن با embedding"""
        embedding = self.encoder.encode(text).tolist()
        
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "text": text,
                "metadata": metadata or {}
            }
        )
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )
        
        self.logger.info("text_stored", text_length=len(text))
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """جستجوی مشابه"""
        query_embedding = self.encoder.encode(query).tolist()
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit
        )
        
        return [
            {
                "text": r.payload["text"],
                "score": r.score,
                "metadata": r.payload.get("metadata", {})
            }
            for r in results
        ]


# تست
if __name__ == "__main__":
    memory = VectorMemory()
    
    # ذخیره نمونه
    memory.store(
        "NDVI شاخص پوشش گیاهی است که از تصاویر ماهواره‌ای محاسبه می‌شود",
        {"type": "definition", "domain": "remote_sensing"}
    )
    
    memory.store(
        "AquaCrop مدل شبیه‌سازی رشد محصول است که توسط FAO توسعه داده شده",
        {"type": "model", "domain": "agriculture"}
    )
    
    # جستجو
    results = memory.search("شاخص‌های ماهواره‌ای چیست؟", limit=2)
    
    print("\n🔍 Search Results:")
    for r in results:
        print(f"  Score: {r['score']:.3f}")
        print(f"  Text: {r['text'][:100]}...")
        print()