"""
Complete RAG Chain
===================

End-to-end Retrieval-Augmented Generation chain built with LangChain.

Combines:
    - Document retrieval from vector store
    - Context-aware prompt construction
    - LLM-based answer generation with citations

The chain supports both streaming and non-streaming execution modes.

Examples:
    >>> chain = RAGChain()
    >>> answer = await chain.query(
    ...     "What irrigation method is best for wheat in Khuzestan?",
    ...     top_k=5
    ... )
    >>> print(answer)
"""

from __future__ import annotations

import logging
from typing import Any, AsyncIterator, Dict, List, Optional

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableSerializable

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default RAG Prompt Template
# ---------------------------------------------------------------------------

RAG_PROMPT_TEMPLATE: str = """You are an expert AI assistant for Econojin, an agricultural and economic platform.

Use the following retrieved context to answer the user's question. If the context does not contain
enough information to answer, say so honestly and provide general guidance based on your knowledge.

Always cite the source of information when available (source name or document reference).

**Retrieved Context:**
{context}

**User Question:** {question}

**Answer:**"""


class RAGChain:
    """Complete Retrieval-Augmented Generation chain.

    Integrates document retrieval with LLM-based answer generation
    to produce context-aware, cited responses.

    Attributes:
        retriever: Document retrieval component.
        llm: Language model for answer generation.
        prompt_template: Prompt template used for generation.
    """

    def __init__(
        self,
        llm: Optional[Any] = None,
        prompt_template: Optional[str] = None,
        top_k: int = 5,
        min_score: float = 0.1,
    ) -> None:
        """Initialize the RAG chain.

        Args:
            llm: LangChain-compatible language model. Uses LLM factory if None.
            prompt_template: Custom prompt template. Uses default if None.
            top_k: Number of documents to retrieve.
            min_score: Minimum retrieval score threshold.
        """
        self.top_k: int = top_k
        self.min_score: float = min_score
        self._llm: Optional[Any] = llm
        self.prompt_template: str = prompt_template or RAG_PROMPT_TEMPLATE

        # Will be built lazily
        self._chain: Optional[RunnableSerializable] = None
        self._retriever: Optional[Any] = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def retriever(self) -> Any:
        """Lazy-load the Retriever singleton.

        Returns:
            The configured Retriever instance.
        """
        if self._retriever is None:
            from apps.shared_ai.rag.retriever import get_retriever

            self._retriever = get_retriever(
                top_k=self.top_k, min_score=self.min_score
            )
        return self._retriever

    @property
    def llm(self) -> Any:
        """Lazy-load the LLM.

        Returns:
            A LangChain-compatible chat model.

        Raises:
            RuntimeError: If LLM cannot be loaded.
        """
        if self._llm is None:
            try:
                from apps.shared_ai.ai.llm_factory import get_llm

                self._llm = get_llm()
            except Exception as exc:
                logger.error("Failed to load LLM: %s", exc)
                raise RuntimeError(f"LLM initialization failed: {exc}") from exc
        return self._llm

    # ------------------------------------------------------------------
    # Chain building
    # ------------------------------------------------------------------

    def _build_chain(self) -> RunnableSerializable:
        """Build the LangChain RAG chain.

        Returns:
            A compiled LangChain chain.
        """
        prompt: ChatPromptTemplate = ChatPromptTemplate.from_template(
            self.prompt_template
        )

        # Format docs as context string
        def _format_docs(docs: List[Document]) -> str:
            """Convert document list to a formatted context string.

            Args:
                docs: List of LangChain Document objects.

            Returns:
                Concatenated context string.
            """
            parts: List[str] = []
            for i, doc in enumerate(docs):
                source: str = doc.metadata.get("source", f"Document-{i + 1}")
                parts.append(f"[{source}]\n{doc.page_content}")
            return "\n\n---\n\n".join(parts)

        # Retrieval function
        async def _retrieve(query: str) -> List[Document]:
            """Retrieve documents for the query.

            Args:
                query: User query string.

            Returns:
                List of LangChain Document objects.
            """
            results: List[Dict[str, Any]] = self.retriever.retrieve(query=query)
            return [
                Document(
                    page_content=r["text"],
                    metadata=r.get("metadata", {}),
                )
                for r in results
            ]

        # Build the chain
        self._chain = (
            {"context": _retrieve, "question": RunnablePassthrough()}
            | (lambda x: {  # noqa: E731
                "context": _format_docs(x["context"]),
                "question": x["question"],
            })
            | prompt
            | self.llm
            | StrOutputParser()
        )

        logger.info("RAG chain built successfully")
        return self._chain

    @property
    def chain(self) -> RunnableSerializable:
        """Lazy-build the LangChain chain.

        Returns:
            The compiled chain.
        """
        if self._chain is None:
            self._build_chain()
        return self._chain

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def query(
        self,
        question: str,
        top_k: Optional[int] = None,
        min_score: Optional[float] = None,
    ) -> str:
        """Run the RAG pipeline and return a generated answer.

        Args:
            question: User question.
            top_k: Number of documents to retrieve (overrides default).
            min_score: Score threshold (overrides default).

        Returns:
            Generated answer string.

        Raises:
            ValueError: If question is empty.
        """
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")

        if top_k is not None:
            self.top_k = top_k
        if min_score is not None:
            self.min_score = min_score

        logger.info("RAG query: '%s'", question[:100])

        try:
            result: str = await self.chain.ainvoke(question)
            return result.strip()
        except Exception as exc:
            logger.error("RAG query failed: %s", exc)

            # Fallback: generate answer without RAG
            try:
                fallback_result: Any = self.llm.invoke(question)
                content: str = getattr(fallback_result, "content", str(fallback_result))
                return content.strip() or "I could not retrieve relevant documents."
            except Exception as fallback_exc:
                logger.error("Fallback also failed: %s", fallback_exc)
                return (
                    "I encountered an error while processing your question. "
                    "Please try again later."
                )

    async def query_stream(
        self,
        question: str,
    ) -> AsyncIterator[str]:
        """Run the RAG pipeline with streaming output.

        Args:
            question: User question.

        Yields:
            Generated answer chunks as they become available.

        Raises:
            ValueError: If question is empty.
        """
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")

        logger.info("RAG stream query: '%s'", question[:100])

        try:
            async for chunk in self.chain.astream(question):
                yield chunk
        except Exception as exc:
            logger.error("RAG stream failed: %s", exc)
            yield f"\n[RAG error: {exc}]"

    # ------------------------------------------------------------------
    # Document management helpers
    # ------------------------------------------------------------------

    def ingest_documents(
        self,
        texts: List[str],
        metadata_list: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """Ingest documents into the vector store for later retrieval.

        Args:
            texts: List of document texts.
            metadata_list: Optional metadata for each document.

        Returns:
            List of assigned document IDs.
        """
        if metadata_list is None:
            metadata_list = [{"source": "manual_ingest"} for _ in texts]

        return self.retriever.vector_store.add_documents(
            texts=texts, metadata_list=metadata_list
        )

    def ingest_file(self, file_path: str) -> List[str]:
        """Load and ingest a single file into the vector store.

        Args:
            file_path: Path to the document file.

        Returns:
            List of assigned chunk IDs.
        """
        from apps.shared_ai.rag.document_loader import DocumentLoader

        loader: DocumentLoader = DocumentLoader()
        chunks: List[Dict[str, Any]] = loader.load_file(file_path)

        texts: List[str] = [c["content"] for c in chunks]
        metadata_list: List[Dict[str, Any]] = [
            {"source": file_path, **c["metadata"]} for c in chunks
        ]

        return self.retriever.vector_store.add_documents(
            texts=texts, metadata_list=metadata_list
        )

    def get_context(self, query: str, top_k: int = 3) -> str:
        """Retrieve context for a query without generating an answer.

        Useful as a tool for agents that only need the retrieved context.

        Args:
            query: Search query.
            top_k: Number of documents to retrieve.

        Returns:
            Formatted context string.
        """
        return self.retriever.retrieve_context(query=query, top_k=top_k)

    def get_stats(self) -> Dict[str, Any]:
        """Return RAG chain statistics.

        Returns:
            Dict with chain configuration and vector store stats.
        """
        return {
            "top_k": self.top_k,
            "min_score": self.min_score,
            "retriever": self.retriever.get_stats(),
        }


# ---------------------------------------------------------------------------
# Singleton access
# ---------------------------------------------------------------------------

_rag_chain_instance: Optional[RAGChain] = None


def get_rag_chain(
    top_k: int = 5,
    min_score: float = 0.1,
) -> RAGChain:
    """Return the singleton RAGChain instance.

    Args:
        top_k: Default document retrieval count.
        min_score: Default score threshold.

    Returns:
        The global RAGChain instance.
    """
    global _rag_chain_instance
    if _rag_chain_instance is None:
        _rag_chain_instance = RAGChain(top_k=top_k, min_score=min_score)
    return _rag_chain_instance
