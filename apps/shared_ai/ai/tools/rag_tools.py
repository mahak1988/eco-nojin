from langchain_core.tools import tool
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


@tool
async def upload_document(
    content: str,
    title: str,
    user_id: int,
    file_type: str = "txt",
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """آپلود سند به پایگاه دانش RAG با chunking معنایی."""
    logger.info(f"📄 Uploading document: {title}")
    
    try:
        from apps.shared_ai.ai.rag.chunk_optimizer import get_chunker
        from apps.shared_ai.ai.rag.hybrid_search import get_hybrid_search
        
        # Chunking معنایی
        chunker = get_chunker()
        chunks = chunker.semantic_chunk(content)
        
        if not chunks:
            return "❌ هیچ chunkی تولید نشد"
        
        # افزودن به hybrid search
        hybrid_search = get_hybrid_search()
        texts = [chunk["content"] for chunk in chunks]
        metadata_list = []
        
        # ✅ اصلاح: بررسی None بودن metadata
        base_metadata = metadata or {}
        
        for chunk in chunks:
            chunk_metadata = chunk.get("metadata", {}) or {}
            
            meta = {
                **base_metadata,
                **chunk_metadata,
                "user_id": user_id,
                "title": title,
                "file_type": file_type
            }
            metadata_list.append(meta)
        
        logger.info(f"📝 Preparing {len(texts)} chunks for upload...")
        doc_ids = hybrid_search.add_documents(texts, metadata_list)
        
        output = [
            f"✅ سند آپلود شد: {title}",
            "",
            f"📊 آمار:",
            f"   • تعداد chunks: {len(chunks)}",
            f"   • نوع chunking: Semantic",
            f"   • Document IDs: {len(doc_ids)}",
            "",
            f"💡 سند اکنون در جستجوی Hybrid (BM25 + Vector) در دسترس است."
        ]
        
        return "\n".join(output)
    
    except Exception as e:
        logger.error(f"❌ Upload error: {e}", exc_info=True)
        return f"❌ خطا در آپلود سند: {str(e)}"


@tool
async def search_knowledge_base(
    query: str,
    user_id: int,
    top_k: int = 5,
    use_reranking: bool = True
) -> str:
    """
    جستجو در پایگاه دانش RAG با Hybrid Search + Reranking.
    
    Args:
        query: عبارت جستجو
        user_id: شناسه کاربر
        top_k: تعداد نتایج برتر
        use_reranking: استفاده از reranking (پیش‌فرض: True)
    
    Returns:
        نتایج جستجو با امتیاز شباهت
    """
    logger.info(f"🔍 Searching knowledge base: {query[:50]}...")
    
    try:
        from apps.shared_ai.ai.rag.hybrid_search import get_hybrid_search
        
        hybrid_search = get_hybrid_search()
        
        # بررسی وجود اسناد
        if not hybrid_search.documents:
            logger.warning("⚠️ No documents in knowledge base")
            return "❌ پایگاه دانش خالی است. لطفاً ابتدا سند آپلود کنید."
        
        # جستجوی ترکیبی
        results = hybrid_search.search(
            query=query,
            top_k=top_k * 2 if use_reranking else top_k,
            filter_metadata={"user_id": user_id}
        )
        
        if not results:
            return "❌ هیچ نتیجه‌ای یافت نشد"
        
        # Reranking
        if use_reranking and len(results) > 1:
            try:
                from apps.shared_ai.ai.rag.reranker import get_reranker
                reranker = get_reranker()
                results = reranker.rerank(query, results, top_k=top_k)
            except Exception as e:
                logger.warning(f"⚠️ Reranking failed: {e}")
                results = results[:top_k]
        else:
            results = results[:top_k]
        
        output = [
            f"🔍 نتایج جستجو در پایگاه دانش (Hybrid + Reranking):",
            f"📊 تعداد نتایج: {len(results)}",
            ""
        ]
        
        for i, result in enumerate(results, 1):
            score = result.get("rerank_score", result.get("score", 0))
            text = result["text"][:200]
            title = result["metadata"].get("title", "بدون عنوان")
            search_type = result.get("search_type", "unknown")
            
            output.append(f"{i}. **{title}** (امتیاز: {score:.4f}, نوع: {search_type})")
            output.append(f"   {text}...")
            output.append("")
        
        return "\n".join(output)
    
    except Exception as e:
        logger.error(f"❌ Search error: {e}", exc_info=True)
        return f"❌ خطا در جستجو: {str(e)}"


@tool
async def get_rag_context(
    query: str,
    user_id: int,
    top_k: int = 3,
    use_reranking: bool = True
) -> str:
    """
    دریافت context برای ایجنت از پایگاه دانش با Hybrid Search + Reranking.
    
    Args:
        query: سوال کاربر
        user_id: شناسه کاربر
        top_k: تعداد اسناد مرتبط
        use_reranking: استفاده از reranking
    
    Returns:
        Context آماده برای LLM
    """
    logger.info(f"📚 Getting RAG context for: {query[:50]}...")
    
    try:
        from apps.shared_ai.ai.rag.hybrid_search import get_hybrid_search
        
        hybrid_search = get_hybrid_search()
        
        # بررسی وجود اسناد
        if not hybrid_search.documents:
            return ""
        
        # جستجوی ترکیبی
        results = hybrid_search.search(
            query=query,
            top_k=top_k * 2 if use_reranking else top_k,
            filter_metadata={"user_id": user_id}
        )
        
        if not results:
            return ""
        
        # Reranking
        if use_reranking and len(results) > 1:
            try:
                from apps.shared_ai.ai.rag.reranker import get_reranker
                reranker = get_reranker()
                results = reranker.rerank(query, results, top_k=top_k)
            except Exception as e:
                logger.warning(f"⚠️ Reranking failed: {e}")
                results = results[:top_k]
        else:
            results = results[:top_k]
        
        # ساخت context
        context_parts = ["📚 **اطلاعات مرتبط از پایگاه دانش (Hybrid + Reranked):**\n"]
        
        for i, result in enumerate(results, 1):
            text = result["text"]
            title = result["metadata"].get("title", "بدون عنوان")
            score = result.get("rerank_score", result.get("score", 0))
            
            context_parts.append(f"### منبع {i}: {title} (مرتبط: {score:.2f})")
            context_parts.append(text)
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    except Exception as e:
        logger.error(f"❌ Context error: {e}", exc_info=True)
        return ""


@tool
async def delete_document(
    title: str,
    user_id: int
) -> str:
    """حذف سند از پایگاه دانش."""
    logger.info(f"🗑️ Deleting document: {title}")
    
    try:
        from apps.shared_ai.ai.rag.hybrid_search import get_hybrid_search
        
        hybrid_search = get_hybrid_search()
        
        # جستجو برای یافتن document IDs
        results = hybrid_search.search(
            query=title,
            top_k=100,
            filter_metadata={"user_id": user_id, "title": title}
        )
        
        if not results:
            return "❌ سند یافت نشد"
        
        # حذف از vector store
        doc_ids = [result["id"] for result in results]
        hybrid_search.vector_store.delete_documents(doc_ids)
        
        # حذف از BM25
        texts_to_remove = [r["text"] for r in results]
        hybrid_search.documents = [
            doc for doc in hybrid_search.documents
            if doc not in texts_to_remove
        ]
        
        # بازآموزش BM25
        if hybrid_search.documents:
            hybrid_search.bm25.fit(hybrid_search.documents)
        
        output = [
            f"✅ سند حذف شد: {title}",
            "",
            f"📊 آمار:",
            f"   • تعداد chunks حذف شده: {len(doc_ids)}"
        ]
        
        return "\n".join(output)
    
    except Exception as e:
        logger.error(f"❌ Delete error: {e}", exc_info=True)
        return f"❌ خطا در حذف سند: {str(e)}"


@tool
async def get_knowledge_base_stats(user_id: int) -> str:
    """دریافت آمار پایگاه دانش کاربر."""
    logger.info(f"📊 Getting knowledge base stats for user {user_id}")
    
    try:
        from apps.shared_ai.ai.rag.hybrid_search import get_hybrid_search
        
        hybrid_search = get_hybrid_search()
        stats = hybrid_search.vector_store.get_stats()
        
        output = [
            f"📊 آمار پایگاه دانش:",
            "",
            f"🔧 Backend: {stats['backend']}",
            f"📦 Collection: {stats.get('collection', 'N/A')}",
            f"📄 تعداد اسناد: {stats['document_count']}",
            f"📐 Dimension: {stats['dimension']}",
            f"🔍 Hybrid Search: ✅ (BM25 + Vector)",
            f"🎯 Reranking: ✅ (Cross-Encoder)",
            f"📝 Chunking: ✅ (Semantic)"
        ]
        
        return "\n".join(output)
    
    except Exception as e:
        logger.error(f"❌ Stats error: {e}", exc_info=True)
        return f"❌ خطا در دریافت آمار: {str(e)}"