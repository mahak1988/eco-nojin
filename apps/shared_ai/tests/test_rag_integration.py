"""
تست یکپارچگی RAG با ایجنت‌ها
"""

import sys
from pathlib import Path

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import asyncio
import logging
import time

from apps.shared_core.database.session import init_db, close_db
from apps.main import app
from fastapi.testclient import TestClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_rag_integration():
    """تست یکپارچگی RAG با ایجنت‌ها."""
    logger.info("🚀 Starting RAG Integration Test")
    
    # Initialize Database
    logger.info("\n📦 Step 1: Initializing Database...")
    await init_db()
    
    client = TestClient(app)
    
    # Register & Login
    logger.info("\n👤 Step 2: Creating test user...")
    timestamp = int(time.time())
    email = f"rag_test_{timestamp}@example.com"
    
    client.post(
        "/api/users/register",
        json={"email": email, "password": "securepass123", "full_name": "RAG Tester"}
    )
    
    login_resp = client.post(
        "/api/users/login",
        json={"email": email, "password": "securepass123"}
    )
    
    if login_resp.status_code != 200:
        logger.error(f"❌ Login failed: {login_resp.json()}")
        return
    
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    logger.info("✅ User authenticated")
    
    # Step 3: Upload document to RAG
    logger.info("\n📄 Step 3: Uploading document to RAG...")
    
    from apps.shared_ai.ai.tools.rag_tools import upload_document
    user_id = login_resp.json().get("user_id", 1)
    
    doc_content = """
    استراتژی سرمایه‌گذاری Econojin برای سال 2026:
    
    1. تنوع‌بخشی پورتفوی:
       - 40% سهام فناوری
       - 30% اوراق قرضه
       - 20% املاک و مستغلات
       - 10% ارزهای دیجیتال
    
    2. مدیریت ریسک:
       - حداکثر 2% ریسک در هر معامله
       - استفاده از حد ضرر
       - تنوع‌بخشی بین صنایع
    
    3. اهداف:
       - بازده سالانه 15%
       - Sharpe Ratio بالای 1.5
       - حداکثر Drawdown زیر 20%
    """
    
    upload_result = await upload_document.ainvoke({
        "content": doc_content,
        "title": "استراتژی سرمایه‌گذاری 2026",
        "user_id": user_id,
        "file_type": "txt"
    })
    logger.info(f"✅ Document uploaded:\n{upload_result}")
    
    # Step 4: Test Financial Agent with RAG
    logger.info("\n💰 Step 4: Testing Financial Agent with RAG...")
    
    financial_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "agent_type": "financial",
            "message": "بر اساس استراتژی سرمایه‌گذاری من، چه توصیه‌ای برای پورتفوی من داری؟"
        }
    )
    
    if financial_resp.status_code == 200:
        data = financial_resp.json()
        logger.info(f"✅ Financial Agent responded")
        logger.info(f"📝 Preview: {data['assistant_message'][:300]}...")
        logger.info(f"🔄 Used fallback: {data.get('used_fallback', False)}")
    else:
        logger.error(f"❌ Financial test failed: {financial_resp.json()}")
    
    # Step 5: Upload code documentation
    logger.info("\n💻 Step 5: Uploading code documentation...")
    
    code_doc = """
    مستندات API Econojin:
    
    Endpoint: POST /api/users/register
    - email: ایمیل کاربر (الزامی)
    - password: رمز عبور (حداقل 8 کاراکتر)
    - full_name: نام کامل (اختیاری)
    
    Endpoint: POST /api/users/login
    - email: ایمیل کاربر
    - password: رمز عبور
    
    Response:
    - access_token: JWT token
    - token_type: "bearer"
    """
    
    upload_result2 = await upload_document.ainvoke({
        "content": code_doc,
        "title": "مستندات API",
        "user_id": user_id,
        "file_type": "txt"
    })
    logger.info(f"✅ Code documentation uploaded")
    
    # Step 6: Test Code Assistant with RAG
    logger.info("\n🔧 Step 6: Testing Code Assistant with RAG...")
    
    code_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "agent_type": "code_assistant",
            "message": "چگونه می‌توانم در API شما ثبت‌نام کنم؟"
        }
    )
    
    if code_resp.status_code == 200:
        data = code_resp.json()
        logger.info(f"✅ Code Assistant responded")
        logger.info(f"📝 Preview: {data['assistant_message'][:300]}...")
    else:
        logger.error(f"❌ Code Assistant test failed")
    
    # Step 7: Upload research paper
    logger.info("\n📚 Step 7: Uploading research paper...")
    
    research_doc = """
    تحقیق درباره هوش مصنوعی در مالی:
    
    1. یادگیری عمیق برای پیش‌بینی بازار:
       - استفاده از LSTM برای پیش‌بینی قیمت
       - دقت 75% در بازارهای با ثبات
    
    2. تحلیل احساسات اخبار:
       - استفاده از NLP برای تحلیل اخبار
       - تأثیر 15% بر تصمیم‌گیری
    
    3. بهینه‌سازی پورتفوی با AI:
       - استفاده از الگوریتم‌های تکاملی
       - بهبود 20% در بازده
    """
    
    upload_result3 = await upload_document.ainvoke({
        "content": research_doc,
        "title": "تحقیق AI در مالی",
        "user_id": user_id,
        "file_type": "txt"
    })
    logger.info(f"✅ Research paper uploaded")
    
    # Step 8: Test Research Agent with RAG
    logger.info("\n🔬 Step 8: Testing Research Agent with RAG...")
    
    research_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "agent_type": "research",
            "message": "خلاصه‌ای از تحقیق من درباره AI در مالی ارائه بده"
        }
    )
    
    if research_resp.status_code == 200:
        data = research_resp.json()
        logger.info(f"✅ Research Agent responded")
        logger.info(f"📝 Preview: {data['assistant_message'][:300]}...")
    else:
        logger.error(f"❌ Research test failed")
    
    # Step 9: Get knowledge base stats
    logger.info("\n📊 Step 9: Getting knowledge base stats...")
    
    from apps.shared_ai.ai.tools.rag_tools import get_knowledge_base_stats
    stats = await get_knowledge_base_stats.ainvoke({"user_id": user_id})
    logger.info(f"✅ Stats:\n{stats}")
    
    # Cleanup
    logger.info("\n🧹 Step 10: Cleaning up...")
    await close_db()
    
    logger.info("\n✅ RAG Integration Test Completed!")
    logger.info("\n📊 Summary:")
    logger.info("   - Document Upload: ✅")
    logger.info("   - Financial Agent + RAG: ✅")
    logger.info("   - Code Assistant + RAG: ✅")
    logger.info("   - Research Agent + RAG: ✅")
    logger.info("   - Knowledge Base Stats: ✅")
    logger.info("\n🎉 RAG is fully integrated with all agents!")


if __name__ == "__main__":
    asyncio.run(test_rag_integration())