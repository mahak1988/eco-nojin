#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌱 اسکریپت پر کردن دیتابیس آزمون‌های روانشناسی
این اسکریپت ۲۵+ آزمون را همراه با سؤالات نمونه به دیتابیس اضافه می‌کند.
"""
import asyncio
import sys
from pathlib import Path

# اضافه کردن ریشه پروژه به sys.path برای شناسایی ماژول‌ها
ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT))

try:
    from api.core.database import engine, async_session, Base
    from api.modules.psychology.models import PsychTest, PsychQuestion, PsychOption, TestCategory, ScoringType
    from api.modules.psychology.engine import TEST_REGISTRY
    from sqlalchemy import select
except ImportError as e:
    print(f"❌ خطا در وارد کردن ماژول‌ها. مطمئن شوید فایل‌های قبلی ایجاد شده‌اند.\nجزئیات: {e}")
    sys.exit(1)

async def seed_database():
    print("🔄 در حال اتصال به دیتابیس و اطمینان از ساخت جداول...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    print("📝 در حال افزودن آزمون‌ها به دیتابیس...")
    async with async_session() as session:
        count = 0
        for code, meta in TEST_REGISTRY.items():
            # بررسی تکراری نبودن آزمون
            result = await session.execute(select(PsychTest).where(PsychTest.code == code))
            if result.scalar_one_or_none():
                continue
                
            test = PsychTest(
                code=code,
                title=meta["title"],
                category=TestCategory[meta["category"]],
                scoring_type=ScoringType[meta["scoring"]],
                has_subscales=meta.get("subscales") is not None,
                duration_minutes=10,
                description=f"آزمون استاندارد {meta['title']} برای ارزیابی تخصصی"
            )
            session.add(test)
            await session.flush()
            
            # افزودن ۵ سؤال نمونه برای هر آزمون (برای اینکه UI کار کند)
            subscales = meta.get("subscales", ["TOTAL"])
            for i in range(5):
                q = PsychQuestion(
                    test_id=test.id,
                    subscale_code=subscales[i % len(subscales)],
                    question_number=i + 1,
                    text=f"[نمونه] سؤال شماره {i+1} مربوط به {meta['title']}. (در نسخه نهایی، سؤالات استاندارد و علمی جایگزین می‌شوند)",
                    is_reverse_scored=(i % 4 == 0) # هر چهارم سؤال معکوس نمره‌دهی می‌شود
                )
                session.add(q)
                await session.flush()
                
                # گزینه‌های طیف لیکرت ۵ گزینه‌ای
                likert_options = [
                    {"label": "کاملاً مخالفم", "base_score": 1},
                    {"label": "مخالفم", "base_score": 2},
                    {"label": "نظری ندارم", "base_score": 3},
                    {"label": "موافقم", "base_score": 4},
                    {"label": "کاملاً موافقم", "base_score": 5},
                ]
                
                for opt in likert_options:
                    # اگر سؤال معکوس است، نمره برعکس می‌شود (مثلاً ۵ می‌شود ۱)
                    score = 6 - opt["base_score"] if (i % 4 == 0) else opt["base_score"]
                    session.add(PsychOption(
                        question_id=q.id,
                        label=opt["label"],
                        score_value=float(score)
                    ))
            count += 1
            
        await session.commit()
        print(f"✅ با موفقیت {count} آزمون جدید همراه با سؤالات نمونه به دیتابیس اضافه شد!")
        print("💡 اکنون می‌توانید به صفحه http://localhost:3001/psychology بروید و آزمون‌ها را مشاهده و اجرا کنید.")

if __name__ == "__main__":
    try:
        asyncio.run(seed_database())
    except Exception as e:
        print(f"❌ خطا در اجرای اسکریپت: {e}")
        import traceback
        traceback.print_exc()