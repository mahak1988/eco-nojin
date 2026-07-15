import sys
from pathlib import Path

# ==========================================
# Fix Python Path for Direct Execution
# ==========================================
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import asyncio
import logging
from typing import List, Any
from sqlalchemy.orm import Mapped, mapped_column
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.tools import BaseTool

from apps.shared_core.database.session import Base, init_db, close_db, async_session_maker
from apps.shared_core.database.repository import BaseRepository
from apps.shared_ai.ai.base_agent import ModularAgentBuilder
from apps.shared_ai.ai.tools.database_tools import query_database, get_table_schema

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==========================================
# Custom Fake LLM with Tool Support
# ==========================================
class FakeToolCallingModel(FakeMessagesListChatModel):
    """
    یک مدل Fake سفارشی که متد bind_tools را پشتیبانی می‌کند.
    این برای تست ایجنت‌ها بدون نیاز به API Key واقعی استفاده می‌شود.
    """
    def bind_tools(self, tools: List[BaseTool], **kwargs: Any) -> "FakeToolCallingModel":
        """
        شبیه‌سازی اتصال ابزارها به مدل.
        در واقع فقط خود را برمی‌گرداند زیرا responses از قبل تعریف شده‌اند.
        """
        return self

# ==========================================
# Demo Model
# ==========================================
class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    price: Mapped[float] = mapped_column()
    category: Mapped[str] = mapped_column()

class ProductRepository(BaseRepository[Product]):
    def __init__(self, session):
        super().__init__(session, Product)

# ==========================================
# Integration Test
# ==========================================
async def test_integration():
    logger.info("🚀 Starting Integration Test: Repository + Agent")
    
    # 1. Initialize Database
    logger.info("\n📦 Step 1: Initializing Database...")
    await init_db()
    
    # 2. Create Sample Data using Repository
    logger.info("\n📝 Step 2: Creating sample data with Repository...")
    async with async_session_maker() as session:
        product_repo = ProductRepository(session)
        
        await product_repo.create({"name": "لپ‌تاپ ایسوس", "price": 45000000, "category": "الکترونیک"})
        await product_repo.create({"name": "گوشی سامسونگ", "price": 25000000, "category": "الکترونیک"})
        await product_repo.create({"name": "کتاب پایتون", "price": 350000, "category": "کتاب"})
        
        count = await product_repo.count()
        logger.info(f"✅ Created {count} products")
    
    # 3. Test Agent with Database Tools
    logger.info("\n🤖 Step 3: Testing AI Agent with Database Tools...")
    
    # ✅ استفاده از FakeToolCallingModel به جای FakeMessagesListChatModel
    fake_llm = FakeToolCallingModel(
        responses=[
            AIMessage(
                content="",
                tool_calls=[{
                    "name": "query_database",
                    "args": {"sql_query": "SELECT name, price FROM products WHERE category = 'الکترونیک'"},
                    "id": "1"
                }]
            ),
            AIMessage(content="بر اساس کوئری دیتابیس، دو محصول الکترونیکی یافت شد: لپ‌تاپ ایسوس با قیمت ۴۵ میلیون تومان و گوشی سامسونگ با قیمت ۲۵ میلیون تومان.")
        ]
    )
    
    tools = [query_database, get_table_schema]
    agent = ModularAgentBuilder(
        llm=fake_llm,
        tools=tools,
        system_prompt="شما یک دستیار هوشمند برای تحلیل داده‌های فروشگاه هستید."
    )
    
    # 4. Run Agent
    logger.info("\n💬 Step 4: Sending query to Agent...")
    response = await agent.run("محصولات الکترونیکی را لیست کن")
    logger.info(f"\n🎯 Agent Response:\n{response}")
    
    # 5. Cleanup
    logger.info("\n🧹 Step 5: Cleaning up...")
    await close_db()
    
    logger.info("\n✅ Integration Test Completed Successfully!")

if __name__ == "__main__":
    asyncio.run(test_integration())