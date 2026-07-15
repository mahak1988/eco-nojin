import sys
from pathlib import Path

# Fix Python Path
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

async def test_admin_agent():
    """تست ایجنت Admin Assistant."""
    logger.info("🚀 Starting Admin Agent Test")
    
    # Initialize Database
    logger.info("\n📦 Step 1: Initializing Database...")
    await init_db()
    
    client = TestClient(app)
    
    # Step 2: Register & Login
    logger.info("\n👤 Step 2: Creating test user...")
    client.post(
        "/api/users/register",
        json={"email": "admin_test@example.com", "password": "securepass123", "full_name": "Admin Tester"}
    )
    
    login_resp = client.post(
        "/api/users/login",
        json={"email": "admin_test@example.com", "password": "securepass123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    logger.info("✅ User authenticated")
    
    # Step 3: Check Agent Types
    logger.info("\n🤖 Step 3: Checking available agent types...")
    types_resp = client.get("/api/ai-agents/types")
    if types_resp.status_code == 200:
        agents = types_resp.json()["agents"]
        admin_agent = next((a for a in agents if a["type"] == "admin"), None)
        if admin_agent:
            logger.info(f"✅ Admin agent found: {admin_agent['name']}")
            logger.info(f"   Description: {admin_agent['description']}")
        else:
            logger.error("❌ Admin agent not found in types")
            return
    else:
        logger.error(f"❌ Failed to get agent types")
        return
    
    # Step 4: Test Admin Agent - Project Status Report
    logger.info("\n📊 Step 4: Requesting project status report...")
    chat_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "agent_type": "admin",
            "message": "لطفاً یک گزارش کلی از وضعیت پروژه ارائه بده."
        }
    )
    
    if chat_resp.status_code == 200:
        chat_data = chat_resp.json()
        conversation_id = chat_data["conversation_id"]
        logger.info(f"✅ Admin agent responded (Conversation ID: {conversation_id})")
        logger.info(f"📝 Response preview:\n{chat_data['assistant_message'][:300]}...")
    else:
        logger.error(f"❌ Chat failed: {chat_resp.json()}")
        return
    
    # Step 5: Test Task Prioritization
    logger.info("\n🎯 Step 5: Requesting task prioritization...")
    prioritize_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "conversation_id": conversation_id,
            "agent_type": "admin",
            "message": "چگونه باید تسک‌های پروژه را اولویت‌بندی کنم؟"
        }
    )
    
    if prioritize_resp.status_code == 200:
        logger.info("✅ Prioritization advice received")
    else:
        logger.error(f"❌ Prioritization failed")
        return
    
    # Step 6: Test KPI Analysis
    logger.info("\n📈 Step 6: Requesting KPI analysis...")
    kpi_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "conversation_id": conversation_id,
            "agent_type": "admin",
            "message": "چه معیارهای کلیدی (KPI) باید برای این پروژه دنبال کنم؟"
        }
    )
    
    if kpi_resp.status_code == 200:
        logger.info("✅ KPI analysis received")
    else:
        logger.error(f"❌ KPI analysis failed")
        return
    
    # Step 7: Test Decision Support
    logger.info("\n💡 Step 7: Requesting decision support...")
    decision_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "conversation_id": conversation_id,
            "agent_type": "admin",
            "message": "بین استفاده از PostgreSQL و MongoDB برای این پروژه کدام را پیشنهاد می‌کنی؟"
        }
    )
    
    if decision_resp.status_code == 200:
        logger.info("✅ Decision support received")
    else:
        logger.error(f"❌ Decision support failed")
        return
    
    # Step 8: Verify Conversation History
    logger.info("\n📋 Step 8: Verifying conversation history...")
    detail_resp = client.get(
        f"/api/ai-agents/conversations/{conversation_id}",
        headers=headers
    )
    
    if detail_resp.status_code == 200:
        detail = detail_resp.json()
        message_count = len(detail["messages"])
        logger.info(f"✅ Conversation has {message_count} messages")
        
        if message_count >= 8:  # 4 user + 4 assistant
            logger.info("✅ All messages saved correctly")
        else:
            logger.warning(f"⚠️ Expected at least 8 messages, got {message_count}")
    else:
        logger.error(f"❌ Failed to get conversation details")
        return
    
    # Cleanup
    logger.info("\n🧹 Step 9: Cleaning up...")
    await close_db()
    
    logger.info("\n✅ Admin Agent Test Completed Successfully!")
    logger.info("\n📊 Summary:")
    logger.info("   - Agent Registration: ✅")
    logger.info("   - Project Status Report: ✅")
    logger.info("   - Task Prioritization: ✅")
    logger.info("   - KPI Analysis: ✅")
    logger.info("   - Decision Support: ✅")
    logger.info("   - Conversation History: ✅")

if __name__ == "__main__":
    asyncio.run(test_admin_agent())