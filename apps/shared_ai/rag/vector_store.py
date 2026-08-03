"""
Vector Store for RAG Pipeline
==============================

In-memory vector store backed by ChromaDB for storing document
embeddings and performing semantic similarity search.

Features:
    - ChromaDB in-memory backend
    - Automatic collection management
    - Metadata filtering
    - Batch document insertion and deletion

Examples:
    >>> store = VectorStore(collection_name="econojin_docs")
    >>> store.add_documents(["text1", "text2"], [{"source": "a"}, {"source": "b"}])
    >>> results = store.search("best crop for Khuzestan", top_k=5)
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class VectorStore:
    """In-memory vector store using ChromaDB for semantic search.

    Stores document embeddings and enables similarity-based
    retrieval with optional metadata filtering.

    Attributes:
        collection_name: Name of the ChromaDB collection.
        dimension: Embedding vector dimensionality.
    """

    def __init__(
        self,
        collection_name: str = "econojin_documents",
        persist_directory: Optional[str] = None,
    ) -> None:
        """Initialize the ChromaDB vector store.

        Args:
            collection_name: Name of the ChromaDB collection.
            persist_directory: Optional path for persistent storage. If None,
                uses in-memory mode.

        Raises:
            RuntimeError: If ChromaDB is not installed.
        """
        self.collection_name: str = collection_name
        self.persist_directory: Optional[str] = persist_directory
        self._client: Any = None
        self._collection: Any = None
        self._dimension: Optional[int] = None

        self._initialize()

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def _initialize(self) -> None:
        """Initialize the ChromaDB client and collection.

        Raises:
            RuntimeError: If chromadb is not available.
        """
        try:
            import chromadb

            if self.persist_directory:
                self._client = chromadb.PersistentClient(path=self.persist_directory)
                logger.info(
                    "ChromaDB persistent client created: %s", self.persist_directory
                )
            else:
                self._client = chromadb.Client()
                logger.info("ChromaDB in-memory client created")

            # Get or create collection
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )

            logger.info(
                "ChromaDB collection ready: %s (count: %d)",
                self.collection_name,
                self._collection.count(),
            )

        except ImportError:
            raise RuntimeError(
                "chromadb is not installed. Run: pip install chromadb"
            )
        except Exception as exc:
            logger.error("Failed to initialize ChromaDB: %s", exc)
            raise RuntimeError(f"ChromaDB initialization failed: {exc}") from exc

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def dimension(self) -> int:
        """Get the embedding dimension from the embedder.

        Returns:
            Embedding dimensionality.

        Raises:
            RuntimeError: If embedder cannot be loaded.
        """
        if self._dimension is None:
            try:
                from apps.shared_ai.rag.embedder import get_embedder

                embedder = get_embedder()
                self._dimension = embedder.dimension
            except Exception as exc:
                logger.warning("Could not determine dimension: %s", exc)
                self._dimension = 384  # sensible default
        return self._dimension

    def add_documents(
        self,
        texts: List[str],
        metadata_list: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
        embeddings: Optional[List[List[float]]] = None,
    ) -> List[str]:
        """Add documents to the vector store.

        Args:
            texts: List of document texts to store.
            metadata_list: List of metadata dicts (one per text).
            ids: Optional list of document IDs (auto-generated if None).
            embeddings: Optional pre-computed embeddings. Generated if None.

        Returns:
            List of assigned document IDs.

        Raises:
            ValueError: If inputs have mismatched lengths.
        """
        if not texts:
            logger.warning("add_documents called with empty texts list")
            return []

        doc_ids: List[str] = ids or [str(uuid.uuid4()) for _ in texts]

        if len(texts) != len(metadata_list):
            raise ValueError(
                f"Length mismatch: texts={len(texts)}, "
                f"metadata_list={len(metadata_list)}"
            )

        if embeddings is None:
            from apps.shared_ai.rag.embedder import get_embedder

            embedder = get_embedder()
            embeddings = embedder.embed_texts(texts)

        # Convert metadata values to strings for ChromaDB compatibility
        serialized_meta: List[Dict[str, str]] = []
        for meta in metadata_list:
            serialized_meta.append(
                {k: str(v) if not isinstance(v, str) else v for k, v in meta.items()}
            )

        try:
            self._collection.add(
                ids=doc_ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=serialized_meta,
            )

            logger.info(
                "Added %d documents to collection '%s' (total: %d)",
                len(texts),
                self.collection_name,
                self._collection.count(),
            )

        except Exception as exc:
            logger.error("Failed to add documents: %s", exc)
            raise RuntimeError(f"Document insertion failed: {exc}") from exc

        return doc_ids

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        min_score: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """Search for documents semantically similar to the query.

        Args:
            query: Search query text.
            top_k: Maximum number of results to return.
            filter_metadata: Optional metadata filter (key-value pairs).
            min_score: Minimum similarity score threshold (0-1).

        Returns:
            List of result dicts with keys: id, text, score, metadata.

        Raises:
            RuntimeError: If embedding or search fails.
        """
        if not query or not query.strip():
            logger.warning("search called with empty query")
            return []

        try:
            from apps.shared_ai.rag.embedder import get_embedder

            embedder = get_embedder()
            query_embedding: List[float] = embedder.embed_text(query)

            logger.info(
                "Searching collection '%s': query='%s', top_k=%d",
                self.collection_name,
                query[:80],
                top_k,
            )

            # Build optional where filter
            where_filter: Optional[Dict[str, Any]] = None
            if filter_metadata:
                where_filter = {
                    k: str(v) if not isinstance(v, str) else v
                    for k, v in filter_metadata.items()
                }

            chroma_results: Any = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter,
                include=["documents", "metadatas", "distances"],
            )

            # Format results
            results: List[Dict[str, Any]] = []
            if (
                chroma_results
                and chroma_results.get("ids")
                and chroma_results["ids"][0]
            ):
                ids: List[str] = chroma_results["ids"][0]
                documents: List[str] = chroma_results.get("documents", [[]])[0]
                metadatas: List[Dict] = chroma_results.get("metadatas", [[]])[0]
                distances: List[float] = chroma_results.get("distances", [[]])[0]

                for i, doc_id in enumerate(ids):
                    # ChromaDB returns cosine distance (0-2); convert to similarity score
                    distance: float = distances[i] if i < len(distances) else 0.0
                    score: float = 1.0 - (distance / 2.0)  # normalize 0-1

                    if score < min_score:
                        continue

                    results.append(
                        {
                            "id": doc_id,
                            "text": documents[i] if i < len(documents) else "",
                            "score": round(score, 4),
                            "metadata": metadatas[i] if i < len(metadatas) else {},
                        }
                    )

            logger.info(
                "Search results: %d (out of %d requested)", len(results), top_k
            )
            return results

        except Exception as exc:
            logger.error("Search failed: %s", exc)
            raise RuntimeError(f"Vector search failed: {exc}") from exc

    def delete_documents(self, doc_ids: List[str]) -> bool:
        """Delete documents from the vector store.

        Args:
            doc_ids: List of document IDs to remove.

        Returns:
            True if deletion succeeded.
        """
        if not doc_ids:
            return True

        try:
            self._collection.delete(ids=doc_ids)
            logger.info(
                "Deleted %d documents from collection '%s'",
                len(doc_ids),
                self.collection_name,
            )
            return True

        except Exception as exc:
            logger.error("Failed to delete documents: %s", exc)
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Return statistics about the vector store.

        Returns:
            Dictionary with backend info, document count, and collection name.
        """
        try:
            count: int = self._collection.count()
        except Exception:
            count = 0

        return {
            "backend": "chromadb",
            "mode": "persistent" if self.persist_directory else "in-memory",
            "collection": self.collection_name,
            "document_count": count,
            "dimension": self.dimension,
        }

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """Remove all documents from the collection (creates a fresh one)."""
        try:
            self._client.delete_collection(name=self.collection_name)
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info("Collection '%s' cleared", self.collection_name)
        except Exception as exc:
            logger.error("Failed to clear collection: %s", exc)


# ---------------------------------------------------------------------------
# Singleton access
# ---------------------------------------------------------------------------

_vector_store_instance: Optional[VectorStore] = None


def get_vector_store(
    collection_name: str = "econojin_documents",
    persist_directory: Optional[str] = None,
) -> VectorStore:
    """Return the singleton VectorStore instance.

    Args:
        collection_name: Name of the ChromaDB collection.
        persist_directory: Optional persistent storage path.

    Returns:
        The global VectorStore instance.
    """
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore(
            collection_name=collection_name,
            persist_directory=persist_directory,
        )
    return _vector_store_instance
