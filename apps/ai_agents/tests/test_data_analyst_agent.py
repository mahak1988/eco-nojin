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

async def test_data_analyst_agent():
    """تست ایجنت Data Analyst."""
    logger.info("🚀 Starting Data Analyst Agent Test")
    
    # Initialize Database
    logger.info("\n📦 Step 1: Initializing Database...")
    await init_db()
    
    client = TestClient(app)
    
    # Step 2: Register & Login
    logger.info("\n👤 Step 2: Creating test user...")
    client.post(
        "/api/users/register",
        json={"email": "analyst_test@example.com", "password": "securepass123", "full_name": "Data Analyst"}
    )
    
    login_resp = client.post(
        "/api/users/login",
        json={"email": "analyst_test@example.com", "password": "securepass123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    logger.info("✅ User authenticated")
    
    # Step 3: Check Agent Types
    logger.info("\n🤖 Step 3: Checking available agent types...")
    types_resp = client.get("/api/ai-agents/types")
    if types_resp.status_code == 200:
        agents = types_resp.json()["agents"]
        analyst_agent = next((a for a in agents if a["type"] == "data_analyst"), None)
        if analyst_agent:
            logger.info(f"✅ Data Analyst agent found: {analyst_agent['name']}")
            logger.info(f"   Description: {analyst_agent['description']}")
            logger.info(f"   Capabilities: {len(analyst_agent['capabilities'])} items")
        else:
            logger.error("❌ Data Analyst agent not found in types")
            return
    else:
        logger.error(f"❌ Failed to get agent types")
        return
    
    # Step 4: Test Statistical Analysis
    logger.info("\n📊 Step 4: Testing statistical analysis...")
    stats_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "agent_type": "data_analyst",
            "message": "لطفاً آمار توصیفی این داده‌ها را محاسبه کن: {'values': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]}"
        }
    )
    
    if stats_resp.status_code == 200:
        stats_data = stats_resp.json()
        conversation_id = stats_data["conversation_id"]
        logger.info(f"✅ Statistical analysis completed (Conversation ID: {conversation_id})")
        logger.info(f"📝 Response preview:\n{stats_data['assistant_message'][:300]}...")
    else:
        logger.error(f"❌ Statistical analysis failed: {stats_resp.json()}")
        return
    
    # Step 5: Test Correlation Analysis
    logger.info("\n🔗 Step 5: Testing correlation analysis...")
    corr_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "conversation_id": conversation_id,
            "agent_type": "data_analyst",
            "message": "همبستگی بین این دو متغیر را تحلیل کن: {'height': [150, 160, 170, 180, 190], 'weight': [50, 60, 70, 80, 90]}"
        }
    )
    
    if corr_resp.status_code == 200:
        logger.info("✅ Correlation analysis completed")
    else:
        logger.error(f"❌ Correlation analysis failed")
        return
    
    # Step 6: Test Chart Generation
    logger.info("\n📊 Step 6: Testing chart generation...")
    chart_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "conversation_id": conversation_id,
            "agent_type": "data_analyst",
            "message": "یک نمودار خطی از این داده‌ها رسم کن: [10, 25, 18, 30, 45, 40, 55, 60]"
        }
    )
    
    if chart_resp.status_code == 200:
        logger.info("✅ Chart generation completed")
    else:
        logger.error(f"❌ Chart generation failed")
        return
    
    # Step 7: Test Trend Analysis
    logger.info("\n📈 Step 7: Testing trend analysis...")
    trend_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "conversation_id": conversation_id,
            "agent_type": "data_analyst",
            "message": "روند این داده‌ها را تحلیل کن: [100, 110, 120, 135, 150, 170, 190, 210]"
        }
    )
    
    if trend_resp.status_code == 200:
        logger.info("✅ Trend analysis completed")
    else:
        logger.error(f"❌ Trend analysis failed")
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
    else:
        logger.error(f"❌ Failed to get conversation details")
        return
    
    # Cleanup
    logger.info("\n🧹 Step 9: Cleaning up...")
    await close_db()
    
    logger.info("\n✅ Data Analyst Agent Test Completed Successfully!")
    logger.info("\n📊 Summary:")
    logger.info("   - Agent Registration: ✅")
    logger.info("   - Statistical Analysis: ✅")
    logger.info("   - Correlation Analysis: ✅")
    logger.info("   - Chart Generation: ✅")
    logger.info("   - Trend Analysis: ✅")
    logger.info("   - Conversation History: ✅")

if __name__ == "__main__":
    asyncio.run(test_data_analyst_agent())