"""Comprehensive authentication test script"""

import sys
import os

if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

import asyncio
import httpx

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"


async def test_health():
    """Test health endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print(f"[1/6] Health Check: {response.status_code}")
        print(f"        Response: {response.json()}")
        assert response.status_code == 200
        print()


async def test_register():
    """Test user registration"""
    async with httpx.AsyncClient() as client:
        data = {
            "email": "farmer@test.com",
            "password": os.environ.get("TEST_PASSWORD", "secure_default_password"),
            "full_name": "Test Farmer",
            "role": "farmer",
        }
        response = await client.post(f"{API_URL}/auth/register", json=data)
        print(f"[2/6] Register: {response.status_code}")
        print(f"        Response: {response.json()}")
        if response.status_code == 201:
            print("        SUCCESS: User registered!")
        elif response.status_code == 400:
            print("        INFO: User already exists (OK)")
        print()


async def test_login():
    """Test login and get token"""
    async with httpx.AsyncClient() as client:
        data = {
            "email": "admin@econojin.com",
            "password": os.environ.get("TEST_PASSWORD", "secure_default_password"),
        }
        response = await client.post(f"{API_URL}/auth/login", json=data)
        print(f"[3/6] Login: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"        Token: {result['access_token'][:50]}...")
            print(f"        Expires in: {result['expires_in']} seconds")
            print("        SUCCESS: Login successful!")
            print()
            return result['access_token']
        else:
            print(f"        ERROR: {response.json()}")
            print("        HINT: Run seed_admin.py first!")
            print()
            return None


async def test_get_me(token: str):
    """Test get current user"""
    if not token:
        print("[4/6] Get Me: SKIPPED (no token)")
        print()
        return
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get(f"{API_URL}/auth/me", headers=headers)
        print(f"[4/6] Get Me: {response.status_code}")
        if response.status_code == 200:
            user = response.json()
            print(f"        ID: {user['id']}")
            print(f"        Email: {user['email']}")
            print(f"        Name: {user['full_name']}")
            print(f"        Role: {user['role']}")
            print("        SUCCESS!")
        else:
            print(f"        ERROR: {response.json()}")
        print()


async def test_list_users(token: str):
    """Test list users (admin only)"""
    if not token:
        print("[5/6] List Users: SKIPPED (no token)")
        print()
        return
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get(f"{API_URL}/users/", headers=headers)
        print(f"[5/6] List Users: {response.status_code}")
        if response.status_code == 200:
            users = response.json()
            print(f"        Total users: {len(users)}")
            for user in users:
                print(f"        - {user['email']} ({user['role']})")
            print("        SUCCESS!")
        else:
            print(f"        ERROR: {response.json()}")
        print()


async def test_update_profile(token: str):
    """Test update profile"""
    if not token:
        print("[6/6] Update Profile: SKIPPED (no token)")
        print()
        return
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "location": "Tehran, Iran",
            "bio": "Updated via API test",
        }
        response = await client.patch(
            f"{API_URL}/users/me",
            headers=headers,
            json=data,
        )
        print(f"[6/6] Update Profile: {response.status_code}")
        if response.status_code == 200:
            user = response.json()
            print(f"        Location: {user.get('location')}")
            print(f"        Bio: {user.get('bio')}")
            print("        SUCCESS!")
        else:
            print(f"        ERROR: {response.json()}")
        print()


async def main():
    """Run all tests"""
    print("=" * 60)
    print("EcoNojin API - Comprehensive Auth Test")
    print("=" * 60)
    print()
    
    try:
        await test_health()
        await test_register()
        token = await test_login()
        await test_get_me(token)
        await test_list_users(token)
        await test_update_profile(token)
        
        print("=" * 60)
        print("All tests completed!")
        print("=" * 60)
    except Exception as e:
        print(f"ERROR: {e}")
        print("Make sure the API is running: uvicorn app.main:app --reload")


if __name__ == "__main__":
    asyncio.run(main())
