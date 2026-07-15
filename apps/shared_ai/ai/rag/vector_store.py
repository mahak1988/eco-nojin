from typing import List, Dict, Any, Optional
import logging
import os
import uuid

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Vector Store با پشتیبانی از Qdrant و FAISS.
    
    اولویت:
    1. Qdrant Cloud (اگر QDRANT_URL و QDRANT_API_KEY تنظیم شده باشد)
    2. Qdrant Local (اگر QDRANT_HOST تنظیم شده باشد)
    3. FAISS (fallback)
    """
    
    def __init__(self, collection_name: str = "econojin_documents"):
        self.collection_name = collection_name
        self._client = None
        self._backend = None  # "qdrant" or "faiss"
        self._faiss_index = None
        self._faiss_data = []
        
        # Embedding dimension
        from apps.shared_ai.ai.rag.embeddings import get_embedding_model
        self.embedding_model = get_embedding_model()
        self.dimension = self.embedding_model.dimension
        
        # Initialize
        self._initialize()
    
    def _initialize(self):
        """راه‌اندازی vector store."""
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        
        # تلاش برای Qdrant Cloud
        if qdrant_url and qdrant_api_key:
            try:
                from qdrant_client import QdrantClient
                from qdrant_client.http import models
                
                self._client = QdrantClient(
                    url=qdrant_url,
                    api_key=qdrant_api_key,
                    timeout=10.0
                )
                
                # بررسی وجود collection
                collections = self._client.get_collections().collections
                collection_names = [c.name for c in collections]
                
                if self.collection_name not in collection_names:
                    self._client.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=models.VectorParams(
                            size=self.dimension,
                            distance=models.Distance.COSINE
                        )
                    )
                    logger.info(f"✅ Qdrant Cloud collection created: {self.collection_name}")
                else:
                    logger.info(f"✅ Qdrant Cloud collection exists: {self.collection_name}")
                
                self._backend = "qdrant"
                return
            
            except Exception as e:
                logger.warning(f"⚠️ Qdrant Cloud failed: {e}")
        
        # تلاش برای Qdrant Local
        elif qdrant_host:
            try:
                from qdrant_client import QdrantClient
                from qdrant_client.http import models
                
                self._client = QdrantClient(
                    host=qdrant_host,
                    port=qdrant_port,
                    timeout=10.0
                )
                
                # بررسی وجود collection
                collections = self._client.get_collections().collections
                collection_names = [c.name for c in collections]
                
                if self.collection_name not in collection_names:
                    self._client.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=models.VectorParams(
                            size=self.dimension,
                            distance=models.Distance.COSINE
                        )
                    )
                    logger.info(f"✅ Qdrant Local collection created: {self.collection_name}")
                
                self._backend = "qdrant"
                return
            
            except Exception as e:
                logger.warning(f"⚠️ Qdrant Local failed: {e}")
        
        # Fallback به FAISS
        logger.info("🔄 Using FAISS as fallback (in-memory)")
        self._initialize_faiss()
    
    def _initialize_faiss(self):
        """راه‌اندازی FAISS."""
        try:
            import faiss
            import numpy as np
            
            self._faiss_index = faiss.IndexFlatIP(self.dimension)  # Inner product = cosine similarity
            self._faiss_data = []
            self._backend = "faiss"
            logger.info(f"✅ FAISS initialized (dimension: {self.dimension})")
        
        except ImportError:
            logger.error("❌ FAISS not installed. Run: pip install faiss-cpu")
            raise RuntimeError("Neither Qdrant nor FAISS is available")
    
    def add_documents(
        self,
        texts: List[str],
        metadata_list: List[Dict[str, Any]]
    ) -> List[str]:
        """
        افزودن اسناد به vector store.
        
        Returns:
            List of document IDs
        """
        if not texts:
            return []
        
        # تولید embeddings
        embeddings = self.embedding_model.embed_texts(texts)
        
        # تولید IDs
        doc_ids = [str(uuid.uuid4()) for _ in texts]
        
        if self._backend == "qdrant":
            from qdrant_client.http import models
            
            points = [
                models.PointStruct(
                    id=doc_id,
                    vector=embedding,
                    payload={
                        "text": text,
                        **metadata
                    }
                )
                for doc_id, embedding, text, metadata in zip(doc_ids, embeddings, texts, metadata_list)
            ]
            
            self._client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"✅ Added {len(texts)} documents to Qdrant")
        
        elif self._backend == "faiss":
            import numpy as np
            
            embeddings_array = np.array(embeddings, dtype=np.float32)
            self._faiss_index.add(embeddings_array)
            
            for doc_id, text, metadata in zip(doc_ids, texts, metadata_list):
                self._faiss_data.append({
                    "id": doc_id,
                    "text": text,
                    **metadata
                })
            
            logger.info(f"✅ Added {len(texts)} documents to FAISS")
        
        return doc_ids
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        جستجوی برداری.
        
        Returns:
            List of documents with scores
        """
        # تولید embedding برای query
        query_embedding = self.embedding_model.embed_text(query)
        
        results = []
        
        if self._backend == "qdrant":
            from qdrant_client.http import models
            
            search_filter = None
            if filter_metadata:
                conditions = [
                    models.FieldCondition(
                        key=key,
                        match=models.MatchValue(value=value)
                    )
                    for key, value in filter_metadata.items()
                ]
                search_filter = models.Filter(must=conditions)
            
            search_results = self._client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                query_filter=search_filter,
                with_payload=True
            )
            
            for result in search_results:
                results.append({
                    "id": result.id,
                    "text": result.payload.get("text", ""),
                    "score": result.score,
                    "metadata": {k: v for k, v in result.payload.items() if k != "text"}
                })
        
        elif self._backend == "faiss":
            import numpy as np
            
            query_array = np.array([query_embedding], dtype=np.float32)
            scores, indices = self._faiss_index.search(query_array, top_k)
            
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0 and idx < len(self._faiss_data):
                    doc = self._faiss_data[idx]
                    
                    # اعمال filter
                    if filter_metadata:
                        match = all(
                            doc.get(k) == v
                            for k, v in filter_metadata.items()
                        )
                        if not match:
                            continue
                    
                    results.append({
                        "id": doc["id"],
                        "text": doc["text"],
                        "score": float(score),
                        "metadata": {k: v for k, v in doc.items() if k not in ["id", "text"]}
                    })
        
        return results
    
    def delete_documents(self, doc_ids: List[str]) -> bool:
        """حذف اسناد از vector store."""
        if not doc_ids:
            return True
        
        if self._backend == "qdrant":
            self._client.delete(
                collection_name=self.collection_name,
                points_selector=doc_ids
            )
            logger.info(f"✅ Deleted {len(doc_ids)} documents from Qdrant")
        
        elif self._backend == "faiss":
            # FAISS不支持 حذف مستقیم، باید rebuild کنیم
            logger.warning("⚠️ FAISS does not support deletion. Rebuilding index...")
            self._rebuild_faiss(exclude_ids=set(doc_ids))
        
        return True
    
    def _rebuild_faiss(self, exclude_ids: set):
        """بازسازی FAISS index بدون اسناد حذف شده."""
        import faiss
        import numpy as np
        
        # فیلتر کردن داده‌ها
        filtered_data = [
            doc for doc in self._faiss_data
            if doc["id"] not in exclude_ids
        ]
        
        if not filtered_data:
            self._faiss_index = faiss.IndexFlatIP(self.dimension)
            self._faiss_data = []
            return
        
        # استخراج embeddings
        texts = [doc["text"] for doc in filtered_data]
        embeddings = self.embedding_model.embed_texts(texts)
        
        # بازسازی index
        self._faiss_index = faiss.IndexFlatIP(self.dimension)
        embeddings_array = np.array(embeddings, dtype=np.float32)
        self._faiss_index.add(embeddings_array)
        self._faiss_data = filtered_data
    
    def get_stats(self) -> Dict[str, Any]:
        """دریافت آمار vector store."""
        if self._backend == "qdrant":
            collection_info = self._client.get_collection(self.collection_name)
            return {
                "backend": "qdrant",
                "collection": self.collection_name,
                "document_count": collection_info.points_count,
                "dimension": self.dimension
            }
        
        elif self._backend == "faiss":
            return {
                "backend": "faiss",
                "document_count": len(self._faiss_data),
                "dimension": self.dimension
            }
        
        return {"backend": "unknown"}


# Singleton instance
_vector_store_instance = None

def get_vector_store() -> VectorStore:
    """دریافت نمونه singleton از vector store."""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore()
    return _vector_store_instance