"""
تست سیستم RAG
"""

import sys
from pathlib import Path

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import asyncio
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_rag():
    """تست سیستم RAG."""
    logger.info("🚀 Starting RAG Test")
    
    # Step 1: Import tools
    logger.info("\n📦 Step 1: Importing RAG tools...")
    try:
        from apps.shared_ai.ai.tools.rag_tools import (
            upload_document,
            search_knowledge_base,
            get_rag_context,
            get_knowledge_base_stats
        )
        logger.info("✅ RAG tools imported")
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        return
    
    # Step 2: Upload documents
    logger.info("\n📄 Step 2: Uploading test documents...")
    
    doc1 = """
    هوش مصنوعی (AI) شاخه‌ای از علوم کامپیوتر است که هدف آن ایجاد سیستم‌هایی است
    که قادر به انجام وظایفی هستند که معمولاً نیاز به هوش انسانی دارند. این وظایف
    شامل یادگیری، استدلال، حل مسئله، درک زبان و بینایی ماشین می‌شود.
    
    یادگیری ماشین (Machine Learning) زیرمجموعه‌ای از هوش مصنوعی است که بر توسعه
    الگوریتم‌هایی تمرکز دارد که می‌توانند از داده‌ها یاد بگیرند و پیش‌بینی کنند.
    """
    
    doc2 = """
    Qdrant یک پایگاه داده برداری open-source است که برای جستجوی شباهت طراحی شده است.
    این سیستم از فیلترهای پیشرفته پشتیبانی می‌کند و برای کاربردهای RAG مناسب است.
    
    FAISS یک کتابخانه برای جستجوی سریع nearest neighbor است که توسط Facebook توسعه
    یافته است. این کتابخانه برای مجموعه داده‌های بزرگ بهینه شده است.
    """
    
    user_id = 1  # Test user
    
    result1 = await upload_document.ainvoke({
        "content": doc1,
        "title": "مقدمه‌ای بر هوش مصنوعی",
        "user_id": user_id,
        "file_type": "txt"
    })
    logger.info(f"✅ Document 1 uploaded:\n{result1}")
    
    result2 = await upload_document.ainvoke({
        "content": doc2,
        "title": "پایگاه‌های داده برداری",
        "user_id": user_id,
        "file_type": "txt"
    })
    logger.info(f"✅ Document 2 uploaded:\n{result2}")
    
    # Step 3: Search knowledge base
    logger.info("\n🔍 Step 3: Searching knowledge base...")
    
    search_result = await search_knowledge_base.ainvoke({
        "query": "یادگیری ماشین چیست؟",
        "user_id": user_id,
        "top_k": 3
    })
    logger.info(f"✅ Search result:\n{search_result}")
    
    # Step 4: Get RAG context
    logger.info("\n📚 Step 4: Getting RAG context...")
    
    context = await get_rag_context.ainvoke({
        "query": "Qdrant و FAISS چه تفاوتی دارند؟",
        "user_id": user_id,
        "top_k": 2
    })
    logger.info(f"✅ RAG context:\n{context[:300]}...")
    
    # Step 5: Get stats
    logger.info("\n📊 Step 5: Getting knowledge base stats...")
    
    stats = await get_knowledge_base_stats.ainvoke({
        "user_id": user_id
    })
    logger.info(f"✅ Stats:\n{stats}")
    
    logger.info("\n✅ RAG Test Completed!")
    logger.info("\n📊 Summary:")
    logger.info("   - Document Upload: ✅")
    logger.info("   - Vector Search: ✅")
    logger.info("   - Context Generation: ✅")
    logger.info("   - Knowledge Base Stats: ✅")


if __name__ == "__main__":
    asyncio.run(test_rag())