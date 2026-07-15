from typing import List, Dict, Any
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)


class DocumentLoader:
    """بارگذاری و chunking اسناد."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def load_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """بارگذاری متن و تقسیم به chunks."""
        metadata = metadata or {}
        
        # پاکسازی متن
        text = self._clean_text(text)
        
        # تقسیم به chunks
        chunks = self._split_text(text)
        
        # افزودن metadata
        result = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                **metadata,
                "chunk_index": i,
                "chunk_total": len(chunks),
                "token_count": len(chunk.split())
            }
            
            result.append({
                "content": chunk,
                "metadata": chunk_metadata
            })
        
        logger.info(f"✅ Loaded text: {len(chunks)} chunks")
        return result
    
    def load_file(self, file_path: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """بارگذاری فایل."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_type = path.suffix.lower()
        
        if file_type == ".txt":
            return self._load_txt(file_path, metadata)
        elif file_type == ".md":
            return self._load_markdown(file_path, metadata)
        elif file_type == ".pdf":
            return self._load_pdf(file_path, metadata)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def _load_txt(self, file_path: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """بارگذاری فایل متنی."""
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        metadata = metadata or {}
        metadata["file_type"] = "txt"
        
        return self.load_text(text, metadata)
    
    def _load_markdown(self, file_path: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """بارگذاری فایل Markdown."""
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # حذف Markdown syntax
        text = re.sub(r'#{1,6}\s+', '', text)  # Headers
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.+?)\*', r'\1', text)  # Italic
        text = re.sub(r'`(.+?)`', r'\1', text)  # Code
        
        metadata = metadata or {}
        metadata["file_type"] = "md"
        
        return self.load_text(text, metadata)
    
    def _load_pdf(self, file_path: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """بارگذاری فایل PDF."""
        try:
            import PyPDF2
            
            text = ""
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            metadata = metadata or {}
            metadata["file_type"] = "pdf"
            metadata["page_count"] = len(pdf_reader.pages)
            
            return self.load_text(text, metadata)
        
        except ImportError:
            raise RuntimeError("PyPDF2 not installed. Run: pip install PyPDF2")
    
    def _clean_text(self, text: str) -> str:
        """پاکسازی متن."""
        # حذف کاراکترهای خاص
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text
    
    def _split_text(self, text: str) -> List[str]:
        """تقسیم متن به chunks."""
        words = text.split()
        chunks = []
        
        i = 0
        while i < len(words):
            chunk_words = words[i:i + self.chunk_size]
            chunk = ' '.join(chunk_words)
            chunks.append(chunk)
            
            i += self.chunk_size - self.chunk_overlap
        
        return chunks


# Singleton instance
_document_loader_instance = None

def get_document_loader() -> DocumentLoader:
    """دریافت نمونه singleton از document loader."""
    global _document_loader_instance
    if _document_loader_instance is None:
        _document_loader_instance = DocumentLoader()
    return _document_loader_instance