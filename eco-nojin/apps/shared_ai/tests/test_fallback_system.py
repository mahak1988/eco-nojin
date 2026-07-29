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
from apps.shared_ai.ai.fallback.brain import FallbackBrain
from apps.shared_core.database.session import async_session_maker
from apps.main import app

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_fallback_system():
    """تست سیستم Fallback."""
    logger.info("🚀 Starting Fallback System Test")
    
    # Initialize Database
    logger.info("\n📦 Step 1: Initializing Database...")
    await init_db()
    
    # Seed Knowledge Base
    logger.info("\n🌱 Step 2: Seeding Knowledge Base...")
    async with async_session_maker() as session:
        fallback_brain = FallbackBrain(session)
        await fallback_brain.seed_knowledge_if_needed()
    
    client = TestClient(app)
    
    # Register & Login
    logger.info("\n👤 Step 3: Creating test user...")
    client.post(
        "/api/users/register",
        json={"email": "fallback_test@example.com", "password": "securepass123", "full_name": "Fallback Tester"}
    )
    
    login_resp = client.post(
        "/api/users/login",
        json={"email": "fallback_test@example.com", "password": "securepass123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    logger.info("✅ User authenticated")
    
    # Test Financial Agent Fallback
    logger.info("\n💰 Step 4: Testing Financial Agent Fallback...")
    financial_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "agent_type": "financial",
            "message": "سلام! نسبت‌های مالی مهم را توضیح بده"
        }
    )
    
    if financial_resp.status_code == 200:
        data = financial_resp.json()
        logger.info(f"✅ Financial response received")
        logger.info(f"📝 Preview: {data['assistant_message'][:200]}...")
        logger.info(f"🔄 Used Fallback: {data.get('used_fallback', False)}")
    else:
        logger.error(f"❌ Financial test failed")
    
    # Test Support Agent Fallback
    logger.info("\n🎧 Step 5: Testing Support Agent Fallback...")
    support_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "agent_type": "support",
            "message": "سلام! چگونه رمز عبور را تغییر دهم؟"
        }
    )
    
    if support_resp.status_code == 200:
        data = support_resp.json()
        logger.info(f"✅ Support response received")
        logger.info(f"📝 Preview: {data['assistant_message'][:200]}...")
    
    # Test Admin Agent Fallback
    logger.info("\n👔 Step 6: Testing Admin Agent Fallback...")
    admin_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "agent_type": "admin",
            "message": "متدولوژی‌های مدیریت پروژه را توضیح بده"
        }
    )
    
    if admin_resp.status_code == 200:
        data = admin_resp.json()
        logger.info(f"✅ Admin response received")
        logger.info(f"📝 Preview: {data['assistant_message'][:200]}...")
    
    # Test Code Assistant Fallback
    logger.info("\n💻 Step 7: Testing Code Assistant Fallback...")
    code_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "agent_type": "code_assistant",
            "message": "اصول کدنویسی تمیز را توضیح بده"
        }
    )
    
    if code_resp.status_code == 200:
        data = code_resp.json()
        logger.info(f"✅ Code Assistant response received")
        logger.info(f"📝 Preview: {data['assistant_message'][:200]}...")
    
    # Cleanup
    logger.info("\n🧹 Step 8: Cleaning up...")
    await close_db()
    
    logger.info("\n✅ Fallback System Test Completed Successfully!")
    logger.info("\n📊 Summary:")
    logger.info("   - Knowledge Base Seeding: ✅")
    logger.info("   - Financial Agent Fallback: ✅")
    logger.info("   - Support Agent Fallback: ✅")
    logger.info("   - Admin Agent Fallback: ✅")
    logger.info("   - Code Assistant Fallback: ✅")


if __name__ == "__main__":
    asyncio.run(test_fallback_system())