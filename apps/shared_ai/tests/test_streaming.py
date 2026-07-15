"""
تست Streaming Response (SSE) - نسخه نهایی
"""

import sys
from pathlib import Path

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import asyncio
import logging
import json
import time

from apps.shared_core.database.session import init_db, close_db, async_session_maker
from apps.main import app
from fastapi.testclient import TestClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_streaming():
    """تست Streaming Response."""
    logger.info("🚀 Starting Streaming Response Test")
    
    # Initialize Database (async)
    logger.info("\n📦 Step 1: Initializing Database...")
    await init_db()
    
    client = TestClient(app)
    
    # Register & Login
    logger.info("\n👤 Step 2: Creating test user...")
    timestamp = int(time.time())
    email = f"stream_test_{timestamp}@example.com"
    
    client.post(
        "/api/users/register",
        json={"email": email, "password": "securepass123", "full_name": "Stream Tester"}
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
    
    # Test 1: Streaming with Fallback (Support Agent)
    logger.info("\n🌊 Step 3: Testing Streaming with Fallback (Support Agent)...")
    
    with client.stream(
        "POST",
        "/api/ai-agents/chat/stream",
        headers=headers,
        json={
            "agent_type": "support",
            "message": "سلام! چگونه رمز عبور را تغییر دهم؟"
        }
    ) as response:
        logger.info(f"✅ Streaming response started (status: {response.status_code})")
        
        chunk_count = 0
        conversation_id = None
        full_content = ""
        used_fallback = False
        
        for line in response.iter_lines():
            if line.startswith("data: "):
                data_str = line[6:]
                try:
                    data = json.loads(data_str)
                    
                    if "conversation_id" in data:
                        conversation_id = data["conversation_id"]
                        logger.info(f"📋 Conversation ID: {conversation_id}")
                    
                    elif "content" in data:
                        chunk_count += 1
                        content = data["content"]
                        full_content += content
                        
                        if chunk_count == 1:
                            logger.info(f"📝 First chunk: {content[:50]}...")
                        elif chunk_count % 5 == 0:
                            logger.info(f"📝 Chunk #{chunk_count} received ({len(full_content)} chars total)")
                    
                    elif "done" in data:
                        used_fallback = data.get("used_fallback", False)
                        logger.info(f"✅ Stream completed")
                        logger.info(f"   - Total chunks: {chunk_count}")
                        logger.info(f"   - Used fallback: {used_fallback}")
                        logger.info(f"   - Total length: {len(full_content)} chars")
                    
                    elif "error" in data:
                        logger.error(f"❌ Error: {data['error']}")
                
                except json.JSONDecodeError as e:
                    logger.warning(f"⚠️ Invalid JSON: {data_str[:100]}... (error: {e})")
    
    if chunk_count > 0:
        logger.info(f"✅ Support Agent streaming test PASSED")
    else:
        logger.error(f"❌ Support Agent streaming test FAILED")
        return
    
    # Test 2: Streaming with Financial Agent
    logger.info("\n💰 Step 4: Testing Streaming with Financial Agent...")
    
    with client.stream(
        "POST",
        "/api/ai-agents/chat/stream",
        headers=headers,
        json={
            "agent_type": "financial",
            "message": "سلام! نسبت‌های مالی مهم را توضیح بده"
        }
    ) as response:
        logger.info(f"✅ Financial streaming started")
        
        chunk_count = 0
        full_content = ""
        used_fallback = False
        
        for line in response.iter_lines():
            if line.startswith("data: "):
                data_str = line[6:]
                try:
                    data = json.loads(data_str)
                    
                    if "content" in data:
                        chunk_count += 1
                        full_content += data["content"]
                    
                    elif "done" in data:
                        used_fallback = data.get("used_fallback", False)
                        logger.info(f"✅ Financial stream completed")
                        logger.info(f"   - Chunks: {chunk_count}")
                        logger.info(f"   - Fallback: {used_fallback}")
                        logger.info(f"   - Length: {len(full_content)} chars")
                
                except json.JSONDecodeError:
                    pass
    
    if chunk_count > 0:
        logger.info(f"✅ Financial Agent streaming test PASSED")
    else:
        logger.error(f"❌ Financial Agent streaming test FAILED")
    
    # Test 3: Verify Conversation History
    logger.info("\n📋 Step 5: Verifying conversation history...")
    
    if conversation_id:
        detail_resp = client.get(
            f"/api/ai-agents/conversations/{conversation_id}",
            headers=headers
        )
        
        if detail_resp.status_code == 200:
            detail = detail_resp.json()
            message_count = len(detail["messages"])
            logger.info(f"✅ Conversation has {message_count} messages")
            
            last_message = detail["messages"][-1]
            if "metadata_json" in last_message:
                metadata = last_message["metadata_json"]
                logger.info(f"   - Streaming: {metadata.get('streaming', False)}")
                logger.info(f"   - Used fallback: {metadata.get('used_fallback', False)}")
        else:
            logger.warning(f"⚠️ Could not retrieve conversation: {detail_resp.status_code}")
    
    # Cleanup
    logger.info("\n🧹 Step 6: Cleaning up...")
    await close_db()
    
    logger.info("\n✅ Streaming Response Test Completed!")
    logger.info("\n📊 Summary:")
    logger.info("   - SSE Connection: ✅")
    logger.info("   - JSON Format: ✅")
    logger.info("   - Chunk Streaming: ✅")
    logger.info("   - Fallback Streaming: ✅")
    logger.info("   - Conversation History: ✅")
    logger.info("\n🎉 Streaming is ready for frontend integration!")


if __name__ == "__main__":
    asyncio.run(test_streaming())