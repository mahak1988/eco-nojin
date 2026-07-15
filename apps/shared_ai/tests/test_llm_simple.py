import sys
from pathlib import Path

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import asyncio
import logging
import os
from apps.shared_ai.ai.llm_factory import LLMFactory

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_llm_factory():
    """تست کارخانه LLM با providerهای مختلف."""
    logger.info("🚀 Starting LLM Factory Test")
    
    # Step 1: List Providers
    logger.info("\n📋 Step 1: Listing available providers...")
    providers = LLMFactory.list_providers()
    
    for name, info in providers.items():
        status_icon = "✅" if info["status"] == "available" else "⚠️"
        logger.info(f"  {status_icon} {info['name']}: {info['status']}")
        logger.info(f"     Default Model: {info['default_model']}")
        if info['signup_url']:
            logger.info(f"     Signup: {info['signup_url']}")
    
    # Step 2: Test Current Provider
    logger.info("\n🤖 Step 2: Testing current provider...")
    current_provider = os.getenv("LLM_PROVIDER", "xai")
    logger.info(f"Current provider: {current_provider}")
    
    llm = LLMFactory.create()
    logger.info(f"✅ LLM created: {type(llm).__name__}")
    
    # Step 3: Test Simple Query
    logger.info("\n💬 Step 3: Testing simple query...")
    try:
        from langchain_core.messages import HumanMessage
        
        response = await llm.ainvoke([HumanMessage(content="سلام! خودت را معرفی کن.")])
        logger.info(f"✅ Response: {response.content[:200]}...")
    except Exception as e:
        logger.error(f"❌ Query failed: {e}")
    
    # Step 4: Test Each Provider (if configured)
    logger.info("\n🔄 Step 4: Testing each provider...")
    
    for provider_name in ["groq", "xai", "gemini", "openrouter", "ollama", "fake"]:
        logger.info(f"\n  Testing {provider_name}...")
        try:
            llm = LLMFactory.create(provider=provider_name)
            logger.info(f"    ✅ Created: {type(llm).__name__}")
            
            # Test simple query
            from langchain_core.messages import HumanMessage
            response = await llm.ainvoke([HumanMessage(content="1+1=?")])
            logger.info(f"    ✅ Response: {response.content[:100]}")
        except Exception as e:
            logger.warning(f"    ⚠️ Failed: {e}")
    
    logger.info("\n✅ LLM Factory Test Completed!")

if __name__ == "__main__":
    asyncio.run(test_llm_factory())