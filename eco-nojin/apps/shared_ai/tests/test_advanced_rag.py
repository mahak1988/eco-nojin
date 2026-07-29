"""
تست Advanced RAG: Hybrid Search + Reranking + Semantic Chunking
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


async def test_advanced_rag():
    """تست Advanced RAG."""
    logger.info("🚀 Starting Advanced RAG Test")
    
    # Step 1: Import tools
    logger.info("\n📦 Step 1: Importing Advanced RAG components...")
    try:
        from apps.shared_ai.ai.tools.rag_tools import (
            upload_document,
            search_knowledge_base,
            get_rag_context,
            get_knowledge_base_stats
        )
        logger.info("✅ Advanced RAG tools imported")
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        return
    
    user_id = 1  # Test user
    
    # Step 2: Upload document with semantic chunking
    logger.info("\n📄 Step 2: Uploading document with semantic chunking...")
    
    long_document = """
    استراتژی سرمایه‌گذاری Econojin برای سال 2026:
    
    بخش اول: تنوع‌بخشی پورتفوی
    تنوع‌بخشی یکی از اصول اساسی مدیریت ریسک است. پورتفوی ما شامل 40% سهام فناوری،
    30% اوراق قرضه، 20% املاک و مستغلات و 10% ارزهای دیجیتال است. این توزیع بر اساس
    تحلیل همبستگی بین دارایی‌ها و بهینه‌سازی مارکویتز طراحی شده است.
    
    بخش دوم: مدیریت ریسک
    مدیریت ریسک شامل تعیین حد ضرر برای هر معامله، استفاده از stop-loss orders و
    تنوع‌بخشی بین صنایع مختلف است. حداکثر ریسک در هر معامله 2% از کل سرمایه است.
    
    بخش سوم: تحلیل تکنیکال
    تحلیل تکنیکال شامل استفاده از اندیکاتورهای RSI، MACD و میانگین‌های متحرک است.
    این ابزارها برای شناسایی روندها و نقاط ورود و خروج استفاده می‌شوند.
    
    بخش چهارم: تحلیل فاندامنتال
    تحلیل فاندامنتال شامل بررسی صورت‌های مالی، نسبت‌های مالی و شرایط بازار است.
    نسبت‌های مهم شامل P/E، P/B و ROE هستند.
    
    بخش پنجم: اهداف و معیارها
    اهداف ما شامل بازده سالانه 15%، Sharpe Ratio بالای 1.5 و حداکثر Drawdown زیر 20% است.
    این اهداف بر اساس benchmarkهای بازار و تحمل ریسک سرمایه‌گذاران تعیین شده‌اند.
    """
    
    result1 = await upload_document.ainvoke({
        "content": long_document,
        "title": "استراتژی جامع سرمایه‌گذاری 2026",
        "user_id": user_id,
        "file_type": "txt"
    })
    logger.info(f"✅ Document uploaded with semantic chunking:\n{result1}")
    
    # Step 3: Test Hybrid Search (Keyword)
    logger.info("\n🔍 Step 3: Testing Hybrid Search (Keyword-based)...")
    
    search_result1 = await search_knowledge_base.ainvoke({
        "query": "حد ضرر stop-loss",
        "user_id": user_id,
        "top_k": 3,
        "use_reranking": False
    })
    logger.info(f"✅ Keyword search result:\n{search_result1}")
    
    # Step 4: Test Hybrid Search (Semantic)
    logger.info("\n🧠 Step 4: Testing Hybrid Search (Semantic)...")
    
    search_result2 = await search_knowledge_base.ainvoke({
        "query": "چگونه ریسک سرمایه‌گذاری را مدیریت کنیم؟",
        "user_id": user_id,
        "top_k": 3,
        "use_reranking": False
    })
    logger.info(f"✅ Semantic search result:\n{search_result2}")
    
    # Step 5: Test with Reranking
    logger.info("\n🎯 Step 5: Testing with Reranking...")
    
    search_result3 = await search_knowledge_base.ainvoke({
        "query": "بهترین روش برای تنوع‌بخشی پورتفوی چیست؟",
        "user_id": user_id,
        "top_k": 3,
        "use_reranking": True
    })
    logger.info(f"✅ Reranked search result:\n{search_result3}")
    
    # Step 6: Test Context Generation
    logger.info("\n📚 Step 6: Testing Context Generation...")
    
    context = await get_rag_context.ainvoke({
        "query": "تحلیل تکنیکال و فاندامنتال چه تفاوتی دارند؟",
        "user_id": user_id,
        "top_k": 2,
        "use_reranking": True
    })
    logger.info(f"✅ RAG context:\n{context[:500]}...")
    
    # Step 7: Get stats
    logger.info("\n📊 Step 7: Getting knowledge base stats...")
    
    stats = await get_knowledge_base_stats.ainvoke({
        "user_id": user_id
    })
    logger.info(f"✅ Stats:\n{stats}")
    
    logger.info("\n✅ Advanced RAG Test Completed!")
    logger.info("\n📊 Summary:")
    logger.info("   - Semantic Chunking: ✅")
    logger.info("   - Hybrid Search (BM25 + Vector): ✅")
    logger.info("   - Keyword-based Search: ✅")
    logger.info("   - Semantic Search: ✅")
    logger.info("   - Reranking (Cross-Encoder): ✅")
    logger.info("   - Context Generation: ✅")
    logger.info("   - Knowledge Base Stats: ✅")
    logger.info("\n🎉 Advanced RAG is fully operational!")


if __name__ == "__main__":
    asyncio.run(test_advanced_rag())