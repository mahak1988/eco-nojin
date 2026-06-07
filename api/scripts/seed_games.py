# api/scripts/seed_games.py
"""اسکریپت پر کردن دیتابیس با 30 بازی آموزشی"""
import asyncio
import sys
from pathlib import Path

# مسیر صحیح به ریشه پروژه (سه سطح بالاتر)
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from api.core.database import engine, async_session, Base
from api.modules.games.models import EducationalGame
from api.modules.games.games_database import EDUCATIONAL_GAMES
from sqlalchemy import select

async def seed_games():
    print("🔄 در حال ساخت جداول...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print(f"📝 در حال افزودن {len(EDUCATIONAL_GAMES)} بازی آموزشی...")
    async with async_session() as session:
        count = 0
        for game_data in EDUCATIONAL_GAMES:
            # بررسی تکراری نبودن
            result = await session.execute(
                select(EducationalGame).where(EducationalGame.title == game_data["title"])
            )
            if result.scalar_one_or_none():
                print(f"   ⏭️  تکراری: {game_data['title']}")
                continue
            
            game = EducationalGame(
                title=game_data["title"],
                title_en=game_data["title_en"],
                description=game_data["description"],
                category=game_data["category"],
                embed_url=game_data["embed_url"],
                thumbnail_url=game_data.get("thumbnail"),
                source_website=game_data.get("source", "Educational Games"),
                age_range=game_data.get("age_range", "All ages"),
                duration_minutes=game_data.get("duration_minutes", 15),
                difficulty=game_data.get("difficulty", "medium"),
                educational_objectives=game_data.get("objectives", []),
                skills_developed=game_data.get("skills", []),
                is_active=True,
                requires_login=False
            )
            session.add(game)
            count += 1
            print(f"   ✅ اضافه شد: {game_data['title']}")
        
        await session.commit()
        print(f"\n🎉 {count} بازی آموزشی با موفقیت به دیتابیس اضافه شد!")
        print(f"📊 مجموع بازی‌ها در دیتابیس: {len(EDUCATIONAL_GAMES)}")

if __name__ == "__main__":
    asyncio.run(seed_games())
