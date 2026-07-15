"""
بهینه‌سازی Chunking برای بهبود کیفیت RAG
"""

from typing import List, Dict, Any
import logging
import re

logger = logging.getLogger(__name__)


class SemanticChunker:
    """Chunking معنایی بر اساس جملات و پاراگراف‌ها."""
    
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        separator: str = "\n\n"
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separator = separator
    
    def split_by_sentences(self, text: str) -> List[str]:
        """تقسیم متن به جملات."""
        # تقسیم بر اساس نقطه، علامت سوال و علامت تعجب
        sentences = re.split(r'(?<=[.!?؟])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def split_by_paragraphs(self, text: str) -> List[str]:
        """تقسیم متن به پاراگراف‌ها."""
        paragraphs = text.split(self.separator)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def semantic_chunk(self, text: str) -> List[Dict[str, Any]]:
        """
        Chunking معنایی با حفظ انسجام.
        
        Returns:
            لیست chunks با metadata
        """
        # ابتدا تقسیم به پاراگراف‌ها
        paragraphs = self.split_by_paragraphs(text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para_length = len(para.split())
            
            # اگر پاراگراف به تنهایی بزرگتر از chunk_size است
            if para_length > self.chunk_size:
                # ذخیره chunk فعلی
                if current_chunk:
                    chunk_text = self.separator.join(current_chunk)
                    chunks.append({
                        "content": chunk_text,
                        "metadata": {
                            "chunk_type": "paragraph_group",
                            "word_count": current_length
                        }
                    })
                    current_chunk = []
                    current_length = 0
                
                # تقسیم پاراگراف بزرگ به جملات
                sentences = self.split_by_sentences(para)
                sentence_chunk = []
                sentence_length = 0
                
                for sent in sentences:
                    sent_length = len(sent.split())
                    
                    if sentence_length + sent_length > self.chunk_size:
                        if sentence_chunk:
                            chunk_text = ' '.join(sentence_chunk)
                            chunks.append({
                                "content": chunk_text,
                                "metadata": {
                                    "chunk_type": "sentence_group",
                                    "word_count": sentence_length
                                }
                            })
                        sentence_chunk = [sent]
                        sentence_length = sent_length
                    else:
                        sentence_chunk.append(sent)
                        sentence_length += sent_length
                
                # ذخیره chunk آخر
                if sentence_chunk:
                    chunk_text = ' '.join(sentence_chunk)
                    chunks.append({
                        "content": chunk_text,
                        "metadata": {
                            "chunk_type": "sentence_group",
                            "word_count": sentence_length
                        }
                    })
            
            else:
                # اضافه کردن پاراگراف به chunk فعلی
                if current_length + para_length > self.chunk_size:
                    # ذخیره chunk فعلی
                    if current_chunk:
                        chunk_text = self.separator.join(current_chunk)
                        chunks.append({
                            "content": chunk_text,
                            "metadata": {
                                "chunk_type": "paragraph_group",
                                "word_count": current_length
                            }
                        })
                        
                        # حفظ overlap
                        overlap_text = self.separator.join(current_chunk[-2:])
                        current_chunk = [overlap_text, para]
                        current_length = len(overlap_text.split()) + para_length
                    else:
                        current_chunk = [para]
                        current_length = para_length
                else:
                    current_chunk.append(para)
                    current_length += para_length
        
        # ذخیره chunk آخر
        if current_chunk:
            chunk_text = self.separator.join(current_chunk)
            chunks.append({
                "content": chunk_text,
                "metadata": {
                    "chunk_type": "paragraph_group",
                    "word_count": current_length
                }
            })
        
        logger.info(f"✅ Semantic chunking: {len(chunks)} chunks created")
        return chunks


# Singleton instance
_chunker_instance = None

def get_chunker() -> SemanticChunker:
    """دریافت نمونه singleton از chunker."""
    global _chunker_instance
    if _chunker_instance is None:
        _chunker_instance = SemanticChunker()
    return _chunker_instance