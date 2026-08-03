"""
RAG (Retrieval-Augmented Generation) Module
============================================

Production-grade RAG pipeline for Econojin AI platform.

Submodules:
    - document_loader: Load and chunk documents (PDF, text, markdown)
    - embedder: Generate embeddings using configurable models
    - vector_store: Store and search vectors (ChromaDB in-memory)
    - retriever: Retrieve relevant documents via semantic search
    - chain: Complete RAG chain with LangChain for Q&A

Examples:
    >>> from apps.shared_ai.rag.chain import RAGChain
    >>> chain = RAGChain()
    >>> answer = await chain.query("What is the best crop for Khuzestan?")
"""

from apps.shared_ai.rag.document_loader import DocumentLoader, get_document_loader
from apps.shared_ai.rag.embedder import Embedder, get_embedder
from apps.shared_ai.rag.vector_store import VectorStore, get_vector_store
from apps.shared_ai.rag.retriever import Retriever, get_retriever
from apps.shared_ai.rag.chain import RAGChain, get_rag_chain

__all__ = [
    "DocumentLoader",
    "get_document_loader",
    "Embedder",
    "get_embedder",
    "VectorStore",
    "get_vector_store",
    "Retriever",
    "get_retriever",
    "RAGChain",
    "get_rag_chain",
]
