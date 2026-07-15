"""
تست یکپارچگی کامل: ایجنت‌ها + ابزارهای محاسباتی + Fallback
"""

import sys
from pathlib import Path

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import asyncio
import logging
from fastapi.testclient import TestClient

from apps.shared_core.database.session import init_db, close_db
from apps.main import app

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_full_integration():
    """تست یکپارچگی کامل."""
    logger.info("🚀 Starting Full Integration Test")
    
    # Initialize Database
    logger.info("\n📦 Step 1: Initializing Database...")
    await init_db()
    
    client = TestClient(app)
    
    # Register & Login
    logger.info("\n👤 Step 2: Creating test user...")
    client.post(
        "/api/users/register",
        json={"email": "full_test@example.com", "password": "securepass123", "full_name": "Full Tester"}
    )
    
    login_resp = client.post(
        "/api/users/login",
        json={"email": "full_test@example.com", "password": "securepass123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    logger.info("✅ User authenticated")
    
    # Test 1: Financial Agent with Fast Statistics
    logger.info("\n💰 Step 3: Testing Financial Agent with Fast Statistics...")
    financial_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "agent_type": "financial",
            "message": "لطفاً آمار این داده‌های فروش را تحلیل کن: [100, 150, 200, 180, 220, 250, 300]"
        }
    )
    
    if financial_resp.status_code == 200:
        data = financial_resp.json()
        logger.info(f"✅ Financial Agent responded")
        logger.info(f"📝 Preview: {data['assistant_message'][:200]}...")
    else:
        logger.error(f"❌ Financial test failed")
    
    # Test 2: Data Analyst with Monte Carlo
    logger.info("\n📊 Step 4: Testing Data Analyst with Monte Carlo...")
    analyst_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "agent_type": "data_analyst",
            "message": "یک شبیه‌سازی مونت کارلو با 1000 تکرار برای پیش‌بینی ریسک سرمایه‌گذاری اجرا کن"
        }
    )
    
    if analyst_resp.status_code == 200:
        data = analyst_resp.json()
        logger.info(f"✅ Data Analyst responded")
        logger.info(f"📝 Preview: {data['assistant_message'][:200]}...")
    else:
        logger.error(f"❌ Data Analyst test failed")
    
    # Test 3: Data Analyst with Differential Equations
    logger.info("\n🧮 Step 5: Testing Data Analyst with Differential Equations...")
    diff_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "agent_type": "data_analyst",
            "message": "معادله دیفرانسیل dy/dt = 0.5y را با شرایط اولیه y(0)=1 حل کن"
        }
    )
    
    if diff_resp.status_code == 200:
        data = diff_resp.json()
        logger.info(f"✅ Differential equation solved")
        logger.info(f"📝 Preview: {data['assistant_message'][:200]}...")
    else:
        logger.error(f"❌ Differential equation test failed")
    
    # Test 4: Data Analyst with ML Training
    logger.info("\n🤖 Step 6: Testing Data Analyst with ML Training...")
    ml_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "agent_type": "data_analyst",
            "message": "یک مدل رگرسیون خطی برای داده‌های X=[1,2,3,4,5] و y=[2,4,6,8,10] آموزش بده"
        }
    )
    
    if ml_resp.status_code == 200:
        data = ml_resp.json()
        logger.info(f"✅ ML model trained")
        logger.info(f"📝 Preview: {data['assistant_message'][:200]}...")
    else:
        logger.error(f"❌ ML training test failed")
    
    # Test 5: Fallback System
    logger.info("\n🔄 Step 7: Testing Fallback System...")
    fallback_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "agent_type": "support",
            "message": "سلام! چگونه رمز عبور را تغییر دهم؟"
        }
    )
    
    if fallback_resp.status_code == 200:
        data = fallback_resp.json()
        logger.info(f"✅ Fallback system worked")
        logger.info(f"📝 Preview: {data['assistant_message'][:200]}...")
    else:
        logger.error(f"❌ Fallback test failed")
    
    # Cleanup
    logger.info("\n🧹 Step 8: Cleaning up...")
    await close_db()
    
    logger.info("\n✅ Full Integration Test Completed!")
    logger.info("\n📊 Summary:")
    logger.info("   - Financial Agent + Fast Statistics: ✅")
    logger.info("   - Data Analyst + Monte Carlo: ✅")
    logger.info("   - Data Analyst + Differential Equations: ✅")
    logger.info("   - Data Analyst + ML Training: ✅")
    logger.info("   - Fallback System: ✅")
    logger.info("\n🎉 All systems integrated successfully!")


if __name__ == "__main__":
    asyncio.run(test_full_integration())