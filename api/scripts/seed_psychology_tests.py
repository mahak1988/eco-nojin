# api/scripts/seed_psychology_tests.py
import asyncio
from api.core.database import engine, async_session, Base
from api.modules.psychology.models import PsychTest, PsychQuestion, PsychOption
from api.modules.psychology.test_registry import TEST_REGISTRY

# نمونه سؤالات کامل برای آزمون بیوفیلیا (به عنوان الگو)
BIOPHILIA_QUESTIONS = [
    {"text": "تماشای حیوانات وحشی برای من لذت‌بخش است.", "subscale": "NAT", "reverse": False, "options": [{"label": "کاملاً مخالفم", "score": 1}, {"label": "مخالفم", "score": 2}, {"label": "نظری ندارم", "score": 3}, {"label": "موافقم", "score": 4}, {"label": "کاملاً موافقم", "score": 5}]},
    {"text": "من معتقدم گیاهان و حیوانات حق زندگی مستقل از انسان را دارند.", "subscale": "SYMB", "reverse": False, "options": [{"label": "کاملاً مخالفم", "score": 1}, {"label": "مخالفم", "score": 2}, {"label": "نظری ندارم", "score": 3}, {"label": "موافقم", "score": 4}, {"label": "کاملاً موافقم", "score": 5}]},
    {"text": "حفاظت از محیط زیست فقط زمانی مهم است که به نفع اقتصاد باشد.", "subscale": "UTIL", "reverse": True, "options": [{"label": "کاملاً مخالفم", "score": 5}, {"label": "مخالفم", "score": 4}, {"label": "نظری ندارم", "score": 3}, {"label": "موافقم", "score": 2}, {"label": "کاملاً موافقم", "score": 1}]},
    # ... (برای ۱۲ سؤال دیگر تکرار می‌شود)
]

async def seed_tests():
    async with engine.begin() as conn:
        # ساخت جداول اگر وجود ندارند
        await conn.run_sync(Base.metadata.create_all)
        
    async with async_session() as session:
        for code, meta in TEST_REGISTRY.items():
            # بررسی تکراری نبودن
            from sqlalchemy import select
            result = await session.execute(select(PsychTest).where(PsychTest.code == code))
            if result.scalar_one_or_none():
                continue
                
            test = PsychTest(
                code=code,
                title=meta["title"],
                category=meta["category"],
                scoring_type=meta["scoring_type"],
                has_subscales=meta.get("has_subscales", False),
                duration_minutes=15
            )
            session.add(test)
            await session.flush()
            
            # افزودن سؤالات نمونه (در نسخه نهایی، همه سؤالات از یک فایل JSON بزرگ خوانده می‌شوند)
            if code == "BIOPHILIA":
                for i, q_data in enumerate(BIOPHILIA_QUESTIONS):
                    q = PsychQuestion(
                        test_id=test.id,
                        subscale_code=q_data["subscale"],
                        question_number=i+1,
                        text=q_data["text"],
                        is_reverse_scored=q_data["reverse"]
                    )
                    session.add(q)
                    await session.flush()
                    
                    for opt in q_data["options"]:
                        session.add(PsychOption(question_id=q.id, label=opt["label"], score_value=opt["score"]))
                        
        await session.commit()
        print("✅ دیتابیس آزمون‌ها با موفقیت پر شد!")

if __name__ == "__main__":
    asyncio.run(seed_tests())
