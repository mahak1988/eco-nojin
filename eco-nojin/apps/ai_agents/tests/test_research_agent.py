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

async def test_research_agent():
    """تست ایجنت Research Agent."""
    logger.info("🚀 Starting Research Agent Test")
    
    # Initialize Database
    logger.info("\n📦 Step 1: Initializing Database...")
    await init_db()
    
    client = TestClient(app)
    
    # Step 2: Register & Login
    logger.info("\n👤 Step 2: Creating test user...")
    client.post(
        "/api/users/register",
        json={"email": "research_test@example.com", "password": "securepass123", "full_name": "Research Tester"}
    )
    
    login_resp = client.post(
        "/api/users/login",
        json={"email": "research_test@example.com", "password": "securepass123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    logger.info("✅ User authenticated")
    
    # Step 3: Check Agent Types
    logger.info("\n🤖 Step 3: Checking available agent types...")
    types_resp = client.get("/api/ai-agents/types")
    if types_resp.status_code == 200:
        agents = types_resp.json()["agents"]
        research_agent = next((a for a in agents if a["type"] == "research"), None)
        if research_agent:
            logger.info(f"✅ Research agent found: {research_agent['name']}")
            logger.info(f"   Description: {research_agent['description']}")
            logger.info(f"   Capabilities: {len(research_agent['capabilities'])} items")
        else:
            logger.error("❌ Research agent not found in types")
            return
    else:
        logger.error(f"❌ Failed to get agent types")
        return
    
    # Step 4: Test Web Search
    logger.info("\n🔍 Step 4: Testing web search capability...")
    search_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "agent_type": "research",
            "message": "لطفاً درباره هوش مصنوعی در سال 2026 تحقیق کن و یک گزارش کوتاه ارائه بده."
        }
    )
    
    if search_resp.status_code == 200:
        search_data = search_resp.json()
        conversation_id = search_data["conversation_id"]
        logger.info(f"✅ Research agent responded (Conversation ID: {conversation_id})")
        logger.info(f"📝 Response preview:\n{search_data['assistant_message'][:300]}...")
    else:
        logger.error(f"❌ Search failed: {search_resp.json()}")
        return
    
    # Step 5: Test Summarization
    logger.info("\n📝 Step 5: Testing summarization capability...")
    summarize_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "conversation_id": conversation_id,
            "agent_type": "research",
            "message": "می‌توانی نتایج تحقیق را خلاصه‌تر کنی؟"
        }
    )
    
    if summarize_resp.status_code == 200:
        logger.info("✅ Summarization completed")
    else:
        logger.error(f"❌ Summarization failed")
        return
    
    # Step 6: Test Key Points Extraction
    logger.info("\n🔑 Step 6: Testing key points extraction...")
    keypoints_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "conversation_id": conversation_id,
            "agent_type": "research",
            "message": "نکات کلیدی این تحقیق را استخراج کن."
        }
    )
    
    if keypoints_resp.status_code == 200:
        logger.info("✅ Key points extraction completed")
    else:
        logger.error(f"❌ Key points extraction failed")
        return
    
    # Step 7: Verify Conversation History
    logger.info("\n📋 Step 7: Verifying conversation history...")
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
    logger.info("\n🧹 Step 8: Cleaning up...")
    await close_db()
    
    logger.info("\n✅ Research Agent Test Completed Successfully!")
    logger.info("\n📊 Summary:")
    logger.info("   - Agent Registration: ✅")
    logger.info("   - Web Search: ✅")
    logger.info("   - Summarization: ✅")
    logger.info("   - Key Points Extraction: ✅")
    logger.info("   - Conversation History: ✅")

if __name__ == "__main__":
    asyncio.run(test_research_agent())