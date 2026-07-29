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

async def test_users_module():
    """تست یکپارچگی ماژول کاربران."""
    logger.info("🚀 Starting Users Module Integration Test")
    
    # Initialize Database
    logger.info("\n📦 Step 1: Initializing Database...")
    await init_db()
    
    # Create Test Client
    client = TestClient(app)
    
    # Test 1: Register User
    logger.info("\n📝 Step 2: Testing User Registration...")
    register_response = client.post(
        "/api/users/register",
        json={
            "email": "test@example.com",
            "password": "securepassword123",
            "full_name": "Test User"
        }
    )
    
    if register_response.status_code == 201:
        user_data = register_response.json()
        logger.info(f"✅ User registered: {user_data['email']} (ID: {user_data['id']})")
    else:
        logger.error(f"❌ Registration failed: {register_response.json()}")
        return
    
    # Test 2: Login
    logger.info("\n🔐 Step 3: Testing Login...")
    login_response = client.post(
        "/api/users/login",
        json={
            "email": "test@example.com",
            "password": "securepassword123"
        }
    )
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        access_token = token_data["access_token"]
        logger.info(f"✅ Login successful, token received")
    else:
        logger.error(f"❌ Login failed: {login_response.json()}")
        return
    
    # Test 3: Get Current User
    logger.info("\n👤 Step 4: Testing Get Current User...")
    me_response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    if me_response.status_code == 200:
        current_user = me_response.json()
        logger.info(f"✅ Current user: {current_user['email']}")
    else:
        logger.error(f"❌ Get current user failed: {me_response.json()}")
        return
    
    # Test 4: Update User
    logger.info("\n✏️ Step 5: Testing Update User...")
    update_response = client.put(
        "/api/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"full_name": "Updated Name"}
    )
    
    if update_response.status_code == 200:
        updated_user = update_response.json()
        logger.info(f"✅ User updated: {updated_user['full_name']}")
    else:
        logger.error(f"❌ Update failed: {update_response.json()}")
        return
    
    # Test 5: Unauthorized Access
    logger.info("\n🚫 Step 6: Testing Unauthorized Access...")
    unauthorized_response = client.get("/api/users/me")
    
    if unauthorized_response.status_code == 401:
        logger.info("✅ Unauthorized access correctly blocked")
    else:
        logger.error(f"❌ Security issue: Unauthorized access returned {unauthorized_response.status_code}")
        return
    
    # Cleanup
    logger.info("\n🧹 Step 7: Cleaning up...")
    await close_db()
    
    logger.info("\n✅ Users Module Integration Test Completed Successfully!")
    logger.info("\n📊 Summary:")
    logger.info("   - Registration: ✅")
    logger.info("   - Login: ✅")
    logger.info("   - JWT Authentication: ✅")
    logger.info("   - Profile Management: ✅")
    logger.info("   - Security: ✅")

if __name__ == "__main__":
    asyncio.run(test_users_module())