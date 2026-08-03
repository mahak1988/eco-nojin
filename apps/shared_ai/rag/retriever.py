"""
Retriever for RAG Pipeline
===========================

Retrieves the most relevant documents from the vector store for a
given query. Supports:
    - Top-K semantic search
    - Score threshold filtering
    - Metadata-based filtering
    - Hybrid retrieval strategies

Examples:
    >>> retriever = Retriever()
    >>> docs = retriever.retrieve("crop rotation techniques", top_k=3)
    >>> for doc in docs:
    ...     print(doc["text"][:100], doc["score"])
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class Retriever:
    """Retrieves relevant documents from the vector store.

    Acts as the retrieval layer in the RAG pipeline. Handles
    query embedding generation and semantic search delegation
    to the configured vector store backend.

    Attributes:
        vector_store: The underlying vector store instance.
        top_k: Default number of results to retrieve.
        min_score: Minimum similarity score threshold.
    """

    def __init__(
        self,
        top_k: int = 5,
        min_score: float = 0.1,
        vector_store: Optional[Any] = None,
    ) -> None:
        """Initialize the retriever.

        Args:
            top_k: Default number of results to retrieve.
            min_score: Minimum similarity score threshold (0-1).
            vector_store: Optional pre-configured VectorStore. Created if None.
        """
        self.top_k: int = top_k
        self.min_score: float = min_score
        self._vector_store: Optional[Any] = vector_store

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def vector_store(self) -> Any:
        """Lazy-load the vector store singleton.

        Returns:
            The configured VectorStore instance.
        """
        if self._vector_store is None:
            from apps.shared_ai.rag.vector_store import get_vector_store

            self._vector_store = get_vector_store()
        return self._vector_store

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        min_score: Optional[float] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve the most relevant documents for a query.

        Args:
            query: Search query string.
            top_k: Number of results (overrides instance default).
            min_score: Minimum score threshold (overrides instance default).
            filter_metadata: Optional metadata filter.

        Returns:
            List of result dicts with id, text, score, and metadata.

        Raises:
            ValueError: If query is empty.
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        k: int = top_k if top_k is not None else self.top_k
        threshold: float = min_score if min_score is not None else self.min_score

        logger.info("Retrieving: query='%s', top_k=%d, min_score=%.2f", query[:80], k, threshold)

        try:
            results: List[Dict[str, Any]] = self.vector_store.search(
                query=query,
                top_k=k,
                filter_metadata=filter_metadata,
                min_score=threshold,
            )

            logger.info("Retrieved %d documents for query", len(results))
            return results

        except Exception as exc:
            logger.error("Retrieval failed: %s", exc)
            raise RuntimeError(f"Document retrieval failed: {exc}") from exc

    def retrieve_context(
        self,
        query: str,
        top_k: Optional[int] = None,
        min_score: Optional[float] = None,
        format_as_text: bool = True,
    ) -> str | List[Dict[str, Any]]:
        """Retrieve documents and return formatted context.

        Args:
            query: Search query.
            top_k: Number of results.
            min_score: Score threshold.
            format_as_text: If True, return concatenated text. Otherwise raw results.

        Returns:
            Concatenated context string or raw result list.
        """
        results: List[Dict[str, Any]] = self.retrieve(
            query=query, top_k=top_k, min_score=min_score
        )

        if not format_as_text:
            return results

        if not results:
            return ""

        context_parts: List[str] = []
        for i, doc in enumerate(results):
            source: str = doc.get("metadata", {}).get("source", f"Doc-{i + 1}")
            text: str = doc.get("text", "")
            score: float = doc.get("score", 0.0)
            context_parts.append(
                f"[Source: {source} | Score: {score:.3f}]\n{text}"
            )

        return "\n\n---\n\n".join(context_parts)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def get_stats(self) -> Dict[str, Any]:
        """Return retriever configuration and backend stats.

        Returns:
            Dict with retriever configuration and vector store stats.
        """
        return {
            "top_k": self.top_k,
            "min_score": self.min_score,
            "vector_store": self.vector_store.get_stats(),
        }


# ---------------------------------------------------------------------------
# Singleton access
# ---------------------------------------------------------------------------

_retriever_instance: Optional[Retriever] = None


def get_retriever(
    top_k: int = 5,
    min_score: float = 0.1,
) -> Retriever:
    """Return the singleton Retriever instance.

    Args:
        top_k: Default retrieval count.
        min_score: Default score threshold.

    Returns:
        The global Retriever instance.
    """
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = Retriever(top_k=top_k, min_score=min_score)
    return _retriever_instance
