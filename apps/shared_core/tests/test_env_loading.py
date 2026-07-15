import sys
from pathlib import Path

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import os
from dotenv import load_dotenv

# بارگذاری .env
env_path = Path(".env")
print(f"📁 Checking .env file at: {env_path.absolute()}")
print(f"✅ File exists: {env_path.exists()}")

if env_path.exists():
    load_dotenv(env_path)
    
    print("\n🔑 Loaded Environment Variables:")
    print(f"  LLM_PROVIDER: {os.getenv('LLM_PROVIDER', 'NOT SET')}")
    print(f"  LLM_MODEL: {os.getenv('LLM_MODEL', 'NOT SET')}")
    print(f"  XAI_API_KEY: {'✅ Set' if os.getenv('XAI_API_KEY') else '❌ NOT SET'}")
    print(f"  GROQ_API_KEY: {'✅ Set' if os.getenv('GROQ_API_KEY') else '❌ NOT SET'}")
    print(f"  GOOGLE_API_KEY: {'✅ Set' if os.getenv('GOOGLE_API_KEY') else '❌ NOT SET'}")
    
    if os.getenv('XAI_API_KEY'):
        key = os.getenv('XAI_API_KEY')
        print(f"\n🔐 xAI API Key (first 10 chars): {key[:10]}...")
else:
    print("\n❌ .env file not found!")
    print("💡 Please create .env file in the project root")