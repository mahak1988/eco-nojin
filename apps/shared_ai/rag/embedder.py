"""
Embedder for RAG Pipeline
==========================

Generates vector embeddings from text using configurable models:
    - Sentence Transformers (local, default: all-MiniLM-L6-v2)
    - OpenAI-compatible API embeddings
    - HuggingFace Inference API

All embeddings are normalized for cosine similarity.

Examples:
    >>> embedder = Embedder(model_name="all-MiniLM-L6-v2", provider="sentence_transformers")
    >>> vector = embedder.embed_text("What is the best crop for Iran?")
    >>> vectors = embedder.embed_texts(["text1", "text2", "text3"])
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Supported embedding providers
# ---------------------------------------------------------------------------

SUPPORTED_PROVIDERS: Dict[str, Dict[str, Any]] = {
    "sentence_transformers": {
        "default_model": "all-MiniLM-L6-v2",
        "dimensions": {"all-MiniLM-L6-v2": 384, "all-mpnet-base-v2": 768},
    },
    "openai": {
        "default_model": "text-embedding-3-small",
        "dimensions": {"text-embedding-3-small": 1536, "text-embedding-3-large": 3072},
    },
    "huggingface": {
        "default_model": "sentence-transformers/all-MiniLM-L6-v2",
        "dimensions": {"sentence-transformers/all-MiniLM-L6-v2": 384},
    },
}


class Embedder:
    """Generates text embeddings with multiple provider backends.

    Attributes:
        model_name: Name of the embedding model.
        provider: Backend provider name.
        dimension: Dimensionality of the output vectors.
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        provider: str = "sentence_transformers",
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
    ) -> None:
        """Initialize the embedder.

        Args:
            model_name: Model identifier. Uses provider default if None.
            provider: One of "sentence_transformers", "openai", "huggingface".
            api_key: API key for remote providers.
            api_base: Custom API base URL for OpenAI-compatible endpoints.

        Raises:
            ValueError: If the provider is not supported.
        """
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unsupported provider '{provider}'. "
                f"Available: {list(SUPPORTED_PROVIDERS.keys())}"
            )

        self.provider: str = provider
        self.model_name: str = model_name or SUPPORTED_PROVIDERS[provider]["default_model"]
        self.api_key: Optional[str] = api_key or os.getenv("EMBEDDING_API_KEY")
        self.api_base: Optional[str] = api_base or os.getenv("EMBEDDING_API_BASE")
        self._model: Any = None
        self._dimension: Optional[int] = None

        logger.info(
            "Embedder initialized: provider=%s, model=%s", provider, self.model_name
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def dimension(self) -> int:
        """Return the embedding vector dimensionality.

        Returns:
            Number of dimensions in the embedding vector.
        """
        if self._dimension is not None:
            return self._dimension

        dims: Dict[str, int] = SUPPORTED_PROVIDERS[self.provider].get("dimensions", {})
        self._dimension = dims.get(self.model_name, 384)
        return self._dimension

    @dimension.setter
    def dimension(self, value: int) -> None:
        """Override the detected embedding dimension.

        Args:
            value: Custom dimension to use.
        """
        self._dimension = value

    def embed_text(self, text: str) -> List[float]:
        """Generate an embedding vector for a single text.

        Args:
            text: Input text to embed.

        Returns:
            Embedding vector as a list of floats.

        Raises:
            ValueError: If the text is empty.
        """
        if not text or not text.strip():
            raise ValueError("Cannot embed empty text")
        vectors: List[List[float]] = self.embed_texts([text])
        return vectors[0]

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for a batch of texts.

        Args:
            texts: List of input texts.

        Returns:
            List of embedding vectors.

        Raises:
            ValueError: If the texts list is empty.
        """
        if not texts:
            raise ValueError("Cannot embed empty text list")

        if self.provider == "sentence_transformers":
            return self._embed_sentence_transformers(texts)
        elif self.provider == "openai":
            return self._embed_openai(texts)
        elif self.provider == "huggingface":
            return self._embed_huggingface(texts)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts.

        Args:
            text1: First text.
            text2: Second text.

        Returns:
            Cosine similarity score in [-1, 1].
        """
        emb1: np.ndarray = np.array(self.embed_text(text1))
        emb2: np.ndarray = np.array(self.embed_text(text2))

        dot_product: float = float(np.dot(emb1, emb2))
        norm1: float = float(np.linalg.norm(emb1))
        norm2: float = float(np.linalg.norm(emb2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    # ------------------------------------------------------------------
    # Provider implementations
    # ------------------------------------------------------------------

    def _embed_sentence_transformers(self, texts: List[str]) -> List[List[float]]:
        """Embed using local SentenceTransformer model.

        Args:
            texts: List of texts to embed.

        Returns:
            List of normalized embedding vectors.

        Raises:
            RuntimeError: If sentence-transformers is not installed.
        """
        try:
            from sentence_transformers import SentenceTransformer

            if self._model is None:
                logger.info("Loading SentenceTransformer model: %s", self.model_name)
                self._model = SentenceTransformer(self.model_name)
                self._dimension = self._model.get_sentence_embedding_dimension()
                logger.info("Model loaded (dimension: %d)", self._dimension)

            embeddings: np.ndarray = self._model.encode(
                texts, normalize_embeddings=True, show_progress_bar=False
            )
            return [emb.tolist() for emb in embeddings]

        except ImportError:
            raise RuntimeError(
                "sentence-transformers is not installed. "
                "Run: pip install sentence-transformers"
            )

    def _embed_openai(self, texts: List[str]) -> List[List[float]]:
        """Embed using OpenAI or compatible API.

        Args:
            texts: List of texts to embed.

        Returns:
            List of normalized embedding vectors.

        Raises:
            RuntimeError: If openai package is not installed or API key is missing.
        """
        api_key: Optional[str] = self.api_key or os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY environment variable is not set. "
                "Set EMBEDDING_API_KEY or OPENAI_API_KEY."
            )

        try:
            from openai import OpenAI

            client_kwargs: Dict[str, Any] = {"api_key": api_key}
            if self.api_base:
                client_kwargs["base_url"] = self.api_base

            client: Any = OpenAI(**client_kwargs)

            response: Any = client.embeddings.create(
                model=self.model_name, input=texts
            )

            embeddings: List[List[float]] = []
            for item in response.data:
                vec: np.ndarray = np.array(item.embedding)
                norm: float = float(np.linalg.norm(vec))
                if norm > 0:
                    vec = vec / norm
                embeddings.append(vec.tolist())

            return embeddings

        except ImportError:
            raise RuntimeError(
                "openai package is not installed. Run: pip install openai"
            )

    def _embed_huggingface(self, texts: List[str]) -> List[List[float]]:
        """Embed using HuggingFace Inference API.

        Args:
            texts: List of texts to embed.

        Returns:
            List of normalized embedding vectors.

        Raises:
            RuntimeError: If HF token is not configured or requests fails.
        """
        api_key = self.api_key or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")

        if not api_key:
            raise RuntimeError(
                "HuggingFace token is not set. "
                "Set HF_TOKEN or HUGGINGFACE_TOKEN environment variable."
            )

        try:
            import requests

            api_url: str = (
                f"https://api-inference.huggingface.co/pipeline/"
                f"feature-extraction/{self.model_name}"
            )

            headers: Dict[str, str] = {"Authorization": f"Bearer {api_key}"}
            response = requests.post(
                api_url,
                headers=headers,
                json={"inputs": texts, "options": {"wait_for_model": True}},
                timeout=30,
            )
            response.raise_for_status()

            result: Any = response.json()
            embeddings: List[List[float]] = []

            # HF may return a single list or list of lists
            if isinstance(result[0], list) and isinstance(result[0][0], (int, float)):
                embeddings = [result]
            else:
                embeddings = result

            # Normalize
            normalized: List[List[float]] = []
            for emb in embeddings:
                vec: np.ndarray = np.array(emb)
                norm: float = float(np.linalg.norm(vec))
                if norm > 0:
                    vec = vec / norm
                normalized.append(vec.tolist())

            return normalized

        except ImportError:
            raise RuntimeError(
                "requests package is not installed. Run: pip install requests"
            )


# ---------------------------------------------------------------------------
# Singleton access
# ---------------------------------------------------------------------------

_embedder_instance: Optional[Embedder] = None


def get_embedder(
    model_name: Optional[str] = None,
    provider: Optional[str] = None,
) -> Embedder:
    """Return the singleton Embedder instance.

    Args:
        model_name: Optional model name override.
        provider: Optional provider override (defaults to env EMBEDDING_PROVIDER).

    Returns:
        The global Embedder instance.
    """
    global _embedder_instance
    if _embedder_instance is None:
        resolved_provider: str = provider or os.getenv(
            "EMBEDDING_PROVIDER", "sentence_transformers"
        )
        resolved_model: Optional[str] = model_name or os.getenv("EMBEDDING_MODEL")
        _embedder_instance = Embedder(
            model_name=resolved_model, provider=resolved_provider
        )
    return _embedder_instance
