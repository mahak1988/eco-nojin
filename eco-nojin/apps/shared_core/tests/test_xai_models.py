import sys
from pathlib import Path

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import os
from dotenv import load_dotenv
import httpx
import asyncio

# بارگذاری .env
load_dotenv(project_root / ".env")

async def list_xai_models():
    """لیست کردن تمام مدل‌های موجود در xAI."""
    api_key = os.getenv("XAI_API_KEY")
    
    if not api_key:
        print("❌ XAI_API_KEY not set in .env")
        return
    
    print("🔍 Fetching available models from xAI...")
    print(f"🔑 API Key: {api_key[:15]}...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.x.ai/v1/models",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                models = data.get("data", [])
                
                print(f"\n✅ Found {len(models)} models:")
                print("=" * 60)
                
                for model in models:
                    model_id = model.get("id", "unknown")
                    created = model.get("created", "")
                    owned_by = model.get("owned_by", "unknown")
                    
                    print(f"  📦 {model_id}")
                    print(f"     Owner: {owned_by}")
                    if created:
                        from datetime import datetime
                        created_date = datetime.fromtimestamp(created)
                        print(f"     Created: {created_date.strftime('%Y-%m-%d')}")
                    print()
                
                print("=" * 60)
                print("\n💡 Use one of these model IDs in your .env file:")
                print("   LLM_MODEL=<model-id-from-list>")
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(list_xai_models())