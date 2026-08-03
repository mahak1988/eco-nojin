"""
Document Loader for RAG Pipeline
=================================

Loads and chunks documents from various formats (PDF, text, markdown)
for the Retrieval-Augmented Generation pipeline.

Supports:
    - Plain text files (.txt)
    - Markdown files (.md)
    - PDF files (.pdf) via PyPDF2

Each document is split into overlapping chunks for optimal retrieval.

Examples:
    >>> loader = DocumentLoader(chunk_size=1000, chunk_overlap=200)
    >>> chunks = loader.load_file("reports/crop_analysis.pdf", metadata={"category": "agriculture"})
    >>> for chunk in chunks:
    ...     print(chunk["content"][:100])
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DocumentLoader:
    """Loads and chunks documents for the RAG pipeline.

    Handles multiple file formats and splits content into
    overlapping chunks suitable for embedding and retrieval.

    Attributes:
        chunk_size: Number of words per chunk.
        chunk_overlap: Number of overlapping words between consecutive chunks.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50) -> None:
        """Initialize the document loader with chunking parameters.

        Args:
            chunk_size: Target number of words per chunk.
            chunk_overlap: Number of words to overlap between adjacent chunks.
        """
        self.chunk_size: int = chunk_size
        self.chunk_overlap: int = chunk_overlap

    def load_text(
        self, text: str, metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Load raw text and split it into chunks with metadata.

        Args:
            text: Raw text content to process.
            metadata: Optional metadata dict to attach to each chunk.

        Returns:
            List of chunk dictionaries, each containing "content" and "metadata".
        """
        metadata = metadata or {}

        # Clean and normalize text
        text = self._clean_text(text)

        # Split into chunks
        chunks = self._split_text(text)

        # Attach metadata to each chunk
        result: List[Dict[str, Any]] = []
        for i, chunk in enumerate(chunks):
            chunk_metadata: Dict[str, Any] = {
                **metadata,
                "chunk_index": i,
                "chunk_total": len(chunks),
                "token_count": len(chunk.split()),
            }
            result.append({"content": chunk, "metadata": chunk_metadata})

        logger.info("Loaded text: %d chunks created", len(chunks))
        return result

    def load_file(
        self, file_path: str, metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Load a file by path and chunk its contents.

        Args:
            file_path: Absolute or relative path to the document.
            metadata: Optional metadata for all chunks from this document.

        Returns:
            List of chunk dictionaries with content and metadata.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file format is unsupported.
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_type: str = path.suffix.lower()

        if file_type == ".txt":
            return self._load_txt(file_path, metadata)
        elif file_type == ".md":
            return self._load_markdown(file_path, metadata)
        elif file_type == ".pdf":
            return self._load_pdf(file_path, metadata)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    def _load_txt(
        self, file_path: str, metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Load a plain text file.

        Args:
            file_path: Path to the .txt file.
            metadata: Optional metadata.

        Returns:
            List of chunk dictionaries.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            text: str = f.read()

        metadata = metadata or {}
        metadata["file_type"] = "txt"
        metadata["file_path"] = file_path

        return self.load_text(text, metadata)

    def _load_markdown(
        self, file_path: str, metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Load a Markdown file, stripping formatting syntax.

        Args:
            file_path: Path to the .md file.
            metadata: Optional metadata.

        Returns:
            List of chunk dictionaries.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            text: str = f.read()

        # Strip Markdown formatting for cleaner text
        text = re.sub(r"#{1,6}\s+", "", text)  # Headers
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)  # Bold
        text = re.sub(r"\*(.+?)\*", r"\1", text)  # Italic
        text = re.sub(r"`(.+?)`", r"\1", text)  # Inline code
        text = re.sub(r"```[\s\S]*?```", "", text)  # Code blocks
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # Links
        text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", "", text)  # Images

        metadata = metadata or {}
        metadata["file_type"] = "md"
        metadata["file_path"] = file_path

        return self.load_text(text, metadata)

    def _load_pdf(
        self, file_path: str, metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Load a PDF file using PyPDF2.

        Args:
            file_path: Path to the .pdf file.
            metadata: Optional metadata.

        Returns:
            List of chunk dictionaries.

        Raises:
            RuntimeError: If PyPDF2 is not installed.
        """
        try:
            import PyPDF2

            text_parts: List[str] = []
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    page_text: str = page.extract_text() or ""
                    text_parts.append(page_text)

            text: str = "\n".join(text_parts)

            metadata = metadata or {}
            metadata["file_type"] = "pdf"
            metadata["file_path"] = file_path
            metadata["page_count"] = len(pdf_reader.pages)

            return self.load_text(text, metadata)

        except ImportError:
            raise RuntimeError(
                "PyPDF2 is not installed. Run: pip install PyPDF2"
            )

    def _clean_text(self, text: str) -> str:
        """Normalize whitespace and trim text.

        Args:
            text: Raw input text.

        Returns:
            Cleaned text with normalized whitespace.
        """
        text = re.sub(r"\s+", " ", text)
        text = text.strip()
        return text

    def _split_text(self, text: str) -> List[str]:
        """Split text into overlapping word-level chunks.

        Args:
            text: Cleaned text to split.

        Returns:
            List of text chunks.
        """
        words: List[str] = text.split()
        chunks: List[str] = []

        i: int = 0
        while i < len(words):
            chunk_words: List[str] = words[i : i + self.chunk_size]
            chunk: str = " ".join(chunk_words)
            chunks.append(chunk)

            i += self.chunk_size - self.chunk_overlap

        return chunks


# ---------------------------------------------------------------------------
# Singleton access
# ---------------------------------------------------------------------------

_document_loader_instance: Optional[DocumentLoader] = None


def get_document_loader(
    chunk_size: int = 500, chunk_overlap: int = 50
) -> DocumentLoader:
    """Return the singleton DocumentLoader instance.

    Args:
        chunk_size: Number of words per chunk.
        chunk_overlap: Overlap between chunks.

    Returns:
        The global DocumentLoader instance.
    """
    global _document_loader_instance
    if _document_loader_instance is None:
        _document_loader_instance = DocumentLoader(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
    return _document_loader_instance
