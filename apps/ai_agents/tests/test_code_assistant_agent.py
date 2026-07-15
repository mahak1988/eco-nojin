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

async def test_code_assistant_agent():
    """تست ایجنت Code Assistant."""
    logger.info("🚀 Starting Code Assistant Agent Test")
    
    # Initialize Database
    logger.info("\n📦 Step 1: Initializing Database...")
    await init_db()
    
    client = TestClient(app)
    
    # Step 2: Register & Login
    logger.info("\n👤 Step 2: Creating test user...")
    client.post(
        "/api/users/register",
        json={"email": "code_test@example.com", "password": "securepass123", "full_name": "Code Tester"}
    )
    
    login_resp = client.post(
        "/api/users/login",
        json={"email": "code_test@example.com", "password": "securepass123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    logger.info("✅ User authenticated")
    
    # Step 3: Check Agent Types
    logger.info("\n🤖 Step 3: Checking available agent types...")
    types_resp = client.get("/api/ai-agents/types")
    if types_resp.status_code == 200:
        agents = types_resp.json()["agents"]
        code_agent = next((a for a in agents if a["type"] == "code_assistant"), None)
        if code_agent:
            logger.info(f"✅ Code Assistant agent found: {code_agent['name']}")
            logger.info(f"   Description: {code_agent['description']}")
            logger.info(f"   Capabilities: {len(code_agent['capabilities'])} items")
        else:
            logger.error("❌ Code Assistant agent not found in types")
            return
    else:
        logger.error(f"❌ Failed to get agent types")
        return
    
    # Sample Python code for testing
    sample_code = """
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

class DataProcessor:
    def __init__(self, data):
        self.data = data
    
    def process(self):
        return [x * 2 for x in self.data]
    
    def filter_positive(self):
        return [x for x in self.data if x > 0]
"""
    
    # Step 4: Test Code Analysis
    logger.info("\n🔍 Step 4: Testing code analysis...")
    analysis_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "agent_type": "code_assistant",
            "message": f"لطفاً این کد را تحلیل کن:\n\n```python\n{sample_code}\n```"
        }
    )
    
    if analysis_resp.status_code == 200:
        analysis_data = analysis_resp.json()
        conversation_id = analysis_data["conversation_id"]
        logger.info(f"✅ Code analysis completed (Conversation ID: {conversation_id})")
        logger.info(f"📝 Response preview:\n{analysis_data['assistant_message'][:300]}...")
    else:
        logger.error(f"❌ Code analysis failed: {analysis_resp.json()}")
        return
    
    # Step 5: Test Bug Finding
    logger.info("\n🐛 Step 5: Testing bug finding...")
    buggy_code = """
def process_data(data):
    try:
        result = []
        for item in data:
            result.append(item * 2)
        return result
    except:
        pass
"""
    
    bug_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "conversation_id": conversation_id,
            "agent_type": "code_assistant",
            "message": f"این کد را برای باگ بررسی کن:\n\n```python\n{buggy_code}\n```"
        }
    )
    
    if bug_resp.status_code == 200:
        logger.info("✅ Bug finding completed")
    else:
        logger.error(f"❌ Bug finding failed")
        return
    
    # Step 6: Test Complexity Calculation
    logger.info("\n📈 Step 6: Testing complexity calculation...")
    complex_code = """
def find_duplicates(numbers):
    duplicates = []
    for i in range(len(numbers)):
        for j in range(i+1, len(numbers)):
            if numbers[i] == numbers[j]:
                duplicates.append(numbers[i])
    return duplicates
"""
    
    complexity_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "conversation_id": conversation_id,
            "agent_type": "code_assistant",
            "message": f"پیچیدگی این تابع را محاسبه کن:\n\n```python\n{complex_code}\n```"
        }
    )
    
    if complexity_resp.status_code == 200:
        logger.info("✅ Complexity calculation completed")
    else:
        logger.error(f"❌ Complexity calculation failed")
        return
    
    # Step 7: Test Test Generation
    logger.info("\n🧪 Step 7: Testing test generation...")
    test_gen_resp = client.post(
        "/api/ai-agents/chat",
        headers=headers,
        json={
            "conversation_id": conversation_id,
            "agent_type": "code_assistant",
            "message": f"برای تابع calculate_average تست واحد بنویس:\n\n```python\n{sample_code}\n```"
        }
    )
    
    if test_gen_resp.status_code == 200:
        logger.info("✅ Test generation completed")
    else:
        logger.error(f"❌ Test generation failed")
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
    
    logger.info("\n✅ Code Assistant Agent Test Completed Successfully!")
    logger.info("\n📊 Summary:")
    logger.info("   - Agent Registration: ✅")
    logger.info("   - Code Analysis: ✅")
    logger.info("   - Bug Finding: ✅")
    logger.info("   - Complexity Calculation: ✅")
    logger.info("   - Test Generation: ✅")
    logger.info("   - Conversation History: ✅")

if __name__ == "__main__":
    asyncio.run(test_code_assistant_agent())