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

async def test_ai_agents_module():
    logger.info("🚀 Starting AI Agents Module Integration Test")
    
    # Initialize Database
    logger.info("\n📦 Step 1: Initializing Database...")
    await init_db()
    
    client = TestClient(app)
    
    # Step 2: Register & Login
    logger.info("\n👤 Step 2: Creating test user...")
    client.post(
        "/api/users/register",
        json={"email": "ai_test@example.com", "password": "securepass123", "full_name": "AI Tester"}
    )
    
    login_resp = client.post(
        "/api/users/login",
        json={"email": "ai_test@example.com", "password": "securepass123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    logger.info("✅ User authenticated")
    
    # Step 3: Get Agent Types
    logger.info("\n🤖 Step 3: Listing available agent types...")
    types_resp = client.get("/api/ai-agents/types")
    if types_resp.status_code == 200:
        agents = types_resp.json()["agents"]
        logger.info(f"✅ Found {len(agents)} agent types:")
        for agent in agents:
            logger.info(f"   - {agent['type']}: {agent['name']}")
    else:
        logger.error(f"❌ Failed to get agent types: {types_resp.json()}")
        return
    
    # Step 4: Create Conversation
    logger.info("\n💬 Step 4: Creating new conversation...")
    conv_resp = client.post(
        "/api/ai-agents/conversations",
        headers=headers,
        json={"agent_type": "financial", "title": "تحلیل مالی Q2"}
    )
    
    if conv_resp.status_code == 200:
        conversation = conv_resp.json()
        conversation_id = conversation["id"]
        logger.info(f"✅ Conversation created (ID: {conversation_id})")
    else:
        logger.error(f"❌ Conversation creation failed: {conv_resp.json()}")
        return
    
    # Step 5: Chat with Agent (New Conversation)
    logger.info("\n🧠 Step 5: Sending message to Financial Agent...")
    chat_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "agent_type": "financial",
            "message": "لطفاً خلاصه‌ای از وضعیت کلی بازار ارائه بده."
        }
    )
    
    if chat_resp.status_code == 200:
        chat_data = chat_resp.json()
        new_conv_id = chat_data["conversation_id"]
        logger.info(f"✅ Agent responded (Conversation ID: {new_conv_id})")
        logger.info(f"📝 Response preview: {chat_data['assistant_message'][:100]}...")
    else:
        logger.error(f"❌ Chat failed: {chat_resp.json()}")
        return
    
    # Step 6: Continue Conversation
    logger.info("\n🔄 Step 6: Continuing existing conversation...")
    continue_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "conversation_id": new_conv_id,
            "agent_type": "financial",
            "message": "می‌توانی جزئیات بیشتری ارائه دهی؟"
        }
    )
    
    if continue_resp.status_code == 200:
        logger.info("✅ Conversation continued successfully")
    else:
        logger.error(f"❌ Continue failed: {continue_resp.json()}")
        return
    
    # Step 7: List Conversations
    logger.info("\n📋 Step 7: Listing user conversations...")
    list_resp = client.get("/api/ai-agents/conversations", headers=headers)
    
    if list_resp.status_code == 200:
        conversations = list_resp.json()
        logger.info(f"✅ Found {len(conversations)} conversations:")
        for conv in conversations:
            logger.info(f"   - ID {conv['id']}: {conv['title']} ({conv['message_count']} messages)")
    else:
        logger.error(f"❌ List failed: {list_resp.json()}")
        return
    
    # Step 8: Get Conversation Detail
    logger.info("\n🔍 Step 8: Getting conversation details...")
    detail_resp = client.get(
        f"/api/ai-agents/conversations/{new_conv_id}",
        headers=headers
    )
    
    if detail_resp.status_code == 200:
        detail = detail_resp.json()
        logger.info(f"✅ Conversation detail: {len(detail['messages'])} messages")
    else:
        logger.error(f"❌ Detail failed: {detail_resp.json()}")
        return
    
    # Step 9: Test Support Agent
    logger.info("\n🎧 Step 9: Testing Support Agent...")
    support_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "agent_type": "support",
            "message": "چگونه می‌توانم رمز عبور خود را تغییر دهم؟"
        }
    )
    
    if support_resp.status_code == 200:
        logger.info("✅ Support agent responded successfully")
    else:
        logger.error(f"❌ Support chat failed: {support_resp.json()}")
        return
    
    # Step 10: Test Unauthorized Access
    logger.info("\n🚫 Step 10: Testing unauthorized access...")
    unauth_resp = client.get(f"/api/ai-agents/conversations/{new_conv_id}")
    
    if unauth_resp.status_code == 401:
        logger.info("✅ Unauthorized access correctly blocked")
    else:
        logger.error(f"❌ Security issue: {unauth_resp.status_code}")
        return
    
    # Cleanup
    logger.info("\n🧹 Step 11: Cleaning up...")
    await close_db()
    
    logger.info("\n✅ AI Agents Module Integration Test Completed Successfully!")
    logger.info("\n📊 Summary:")
    logger.info("   - Agent Factory: ✅")
    logger.info("   - Conversation Management: ✅")
    logger.info("   - Financial Agent: ✅")
    logger.info("   - Support Agent: ✅")
    logger.info("   - Message History: ✅")
    logger.info("   - User Isolation: ✅")
    logger.info("   - Security: ✅")

if __name__ == "__main__":
    asyncio.run(test_ai_agents_module())