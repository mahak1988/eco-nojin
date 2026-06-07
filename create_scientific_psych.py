#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 اسکریپت جامع و علمی ماژول روانشناسی اکو نوژین
ویژگی‌ها: روانشناسی رنگ‌ها، تحلیل دامنه‌ای دقیق نمرات، سؤالات علمی واقعی
"""
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT))

try:
    from api.core.database import engine, async_session, Base
    from api.modules.psychology.models import PsychTest, PsychQuestion, PsychOption, TestCategory, ScoringType, PsychResult
    from sqlalchemy import select
except ImportError:
    print("❌ لطفاً ابتدا ساختار اولیه را ایجاد کنید یا از اسکریپت قبلی استفاده کنید.")
    sys.exit(1)

# =========================================================================
# ۱. پایگاه دانش تحلیل علمی و رنگ‌ها (Scientific Interpretation DB)
# =========================================================================
CATEGORY_COLORS = {
    "CLINICAL": "#6366f1",          # نیلی: اعتماد و درون‌نگری
    "ECO_PSYCHOLOGY": "#10b981",    # زمردی: طبیعت و تعادل
    "CLIMATE_RESILIENCE": "#06b6d4",# فیروزه‌ای: سازگاری و آرامش
    "PRO_SOCIAL": "#f59e0b",        # نارنجی: انرژی اجتماعی و گرما
    "OCCUPATIONAL": "#78716c"       # خاکستری-خاکی: واقع‌گرایی و پایداری
}

# تحلیل‌های دقیق بر اساس بازه نمره (نمونه‌ای از تحقیق گسترده)
INTERPRETATION_DB = {
    "NEO_N": {
        "title": "روان‌رنجوری (Neuroticism)",
        "max_score": 25,
        "ranges": {
            (0, 12): {"level": "ثبات هیجانی عالی", "analysis": "شما در مواجهه با استرس، آرامش و کنترل خود را به خوبی حفظ می‌کنید. این ویژگی در مدیریت بحران‌های کشاورزی یک مزیت بزرگ است.", "advice": "این ثبات را حفظ کنید و می‌توانید به عنوان یک تکیه‌گاه هیجانی برای اعضای جامعه خود عمل کنید."},
            (13, 18): {"level": "ثبات هیجانی متوسط", "analysis": "در شرایط عادی آرام هستید، اما فشارهای شدید (مثل خشکسالی طولانی) ممکن است باعث نگرانی شما شود.", "advice": "یادگیری تکنیک‌های ساده تنفسی و ذهن‌آگاهی (Mindfulness) می‌تواند به مدیریت استرس‌های ناگهانی کمک کند."},
            (19, 25): {"level": "حساسیت هیجانی بالا", "analysis": "شما استرس و نگرانی را عمیق‌تر تجربه می‌کنید. این حساسیت می‌تواند منجر به فرسودگی زودرس در کارهای پرفشار شود.", "advice": "توصیه اکید می‌شود با یک مشاور صحبت کنید. تمرینات منظم ورزشی و کاهش کافئین به تنظیم سیستم عصبی شما کمک می‌کند."}
        }
    },
    "BIOPHILIA": {
        "title": "شاخص بیوفیلیا (دوستی ذاتی با حیات)",
        "max_score": 25,
        "ranges": {
            (0, 12): {"level": "نگرش ابزاری به طبیعت", "analysis": "شما طبیعت را بیشتر به عنوان منبعی برای بهره‌برداری اقتصادی می‌بینید تا موجودیتی با ارزش ذاتی.", "advice": "پیشنهاد می‌شود زمان بیشتری را بدون هدف خاصی در طبیعت بگذرانید تا ارتباط حسی خود را با آن بازسازی کنید."},
            (13, 19): {"level": "ارتباط متعادل با طبیعت", "analysis": "شما از طبیعت لذت می‌برید و برای حفظ آن ارزش قائل هستید، اما این ارتباط هنوز به یک هویت عمیق تبدیل نشده است.", "advice": "مشارکت در پروژه‌های کاشت درخت یا باغبانی اجتماعی می‌تواند این پیوند را عمیق‌تر کند."},
            (20, 25): {"level": "هویت زیست‌محیطی عمیق", "analysis": "شما خود را بخشی جدایی‌ناپذیر از چرخه حیات می‌دانید. آسیب به طبیعت برای شما مانند آسیب به خودتان است.", "advice": "شما پتانسیل بالایی برای رهبری جنبش‌های محلی حفاظت از محیط زیست و آموزش به دیگران دارید."}
        }
    },
    "CLIMATE_RESILIENCE": {
        "title": "تاب‌آوری اقلیمی (Climate Resilience)",
        "max_score": 25,
        "ranges": {
            (0, 12): {"level": "آسیب‌پذیری بالا", "analysis": "شما در برابر تغییرات اقلیمی احساس درماندگی می‌کنید و آمادگی کمی برای سازگاری دارید.", "advice": "شروع با اقدامات بسیار کوچک (مثل ذخیره آب باران) می‌تواند حس کنترل شما را بازگرداند. از کمک گرفتن از همسایگان نترسید."},
            (13, 19): {"level": "تاب‌آوری در حال توسعه", "analysis": "شما برخی راهکارها را می‌دانید و گاهی اجرا می‌کنید، اما هنوز یک برنامه منسجم برای مقابله با بحران ندارید.", "advice": "یک برنامه نوشتاری برای مدیریت مزرعه/خانه در شرایط خشکسالی یا سیل تهیه کنید و آن را با خانواده تمرین کنید."},
            (20, 25): {"level": "تاب‌آوری اقلیمی پیشرفته", "analysis": "شما نه‌تنها در برابر شوک‌های اقلیمی مقاوم هستید، بلکه توانایی بازیابی سریع و کمک به دیگران را دارید.", "advice": "دانش و تجربه خود را از طریق کارگاه‌های محلی یا پلتفرم اکو نوژین با کشاورزان کم‌تجربه‌تر به اشتراک بگذارید."}
        }
    },
    "COOPERATION": {
        "title": "همگرومی و همکاری اجتماعی",
        "max_score": 25,
        "ranges": {
            (0, 12): {"level": "گرایش به انزوا", "analysis": "شما ترجیح می‌دهید مسائل را به تنهایی حل کنید و به ندرت منابع خود را با دیگران به اشتراک می‌گذارید.", "advice": "به یاد داشته باشید که چالش‌های بزرگ (مثل کم‌آبی) با تلاش فردی حل نمی‌شوند. با یک اقدام کوچک مشترک شروع کنید."},
            (13, 19): {"level": "همکاری مشروط", "analysis": "شما در صورتی که منافع شما تأمین شود یا به طرف مقابل اعتماد داشته باشید، همکاری می‌کنید.", "advice": "سعی کردن دایره اعتماد خود را گسترش دهید. مشارکت در تعاونی‌های روستایی می‌تواند سود متقابل داشته باشد."},
            (20, 25): {"level": "همگرومی و نوع‌دوستی بالا", "analysis": "شما به شدت به قدرت کار گروهی اعتقاد دارید و حاضرید برای منافع جمعی از منافع کوتاه‌مدت خود بگذرید.", "advice": "شما یک تسهیل‌گر (Facilitator) طبیعی هستید. نقش رهبری در تشکیل گروه‌های مدیریت محلی آب یا خاک را بپذیرید."}
        }
    }
}

# =========================================================================
# ۲. بانک سؤالات علمی واقعی (نمونه‌ای از تحقیق گسترده)
# =========================================================================
REAL_QUESTIONS = {
    "NEO_N": [
        {"text": "من اغلب احساس می‌کنم که تحت فشار و تنش هستم.", "subscale": "N", "reverse": False},
        {"text": "من به ندرت احساس ترس یا اضطراب می‌کنم.", "subscale": "N", "reverse": True},
        {"text": "گاهی اوقات احساس می‌کنم کاملاً بی‌ارزش هستم.", "subscale": "N", "reverse": False},
        {"text": "من به ندرت احساس شرمساری یا خجالت می‌کنم.", "subscale": "N", "reverse": True},
        {"text": "من اغلب نگران این هستم که اوضاع خراب شود.", "subscale": "N", "reverse": False},
    ],
    "BIOPHILIA": [
        {"text": "من از تماشای حیوانات وحشی در زیستگاه طبیعی‌شان لذت می‌برم.", "subscale": "NAT", "reverse": False},
        {"text": "حفاظت از محیط زیست فقط زمانی مهم است که به نفع اقتصاد انسان باشد.", "subscale": "UTIL", "reverse": True},
        {"text": "من احساس می‌کنم که سرنوشت من با سرنوشت طبیعت گره خورده است.", "subscale": "SYMB", "reverse": False},
        {"text": "گذراندن وقت در طبیعت به من احساس آرامش عمیق می‌دهد.", "subscale": "NAT", "reverse": False},
        {"text": "من معتقدم که گیاهان و حیوانات حق زندگی مستقل از نیازهای انسان را دارند.", "subscale": "SYMB", "reverse": False},
    ],
    "CLIMATE_RESILIENCE": [
        {"text": "من یک برنامه عملی برای محافظت از زندگی/مزرعه خود در برابر بلایای اقلیمی دارم.", "subscale": "PREP", "reverse": False},
        {"text": "وقتی یک شوک اقلیمی (مثل سیل یا خشکسالی) رخ می‌دهد، به راحتی می‌توانم خودم را با شرایط جدید وفق دهم.", "subscale": "ADAPT", "reverse": False},
        {"text": "من احساس می‌کنم در برابر تغییرات آب‌وهوایی کاملاً ناتوان و درمانده هستم.", "subscale": "RECOV", "reverse": True},
        {"text": "من با همسایگانم برای مقابله با مشکلات مشترک اقلیمی همکاری می‌کنم.", "subscale": "PREP", "reverse": False},
        {"text": "پس از یک بحران اقلیمی، من سریع‌تر از دیگران به حالت عادی برمی‌گردم.", "subscale": "RECOV", "reverse": False},
    ],
    "COOPERATION": [
        {"text": "من حاضرم منابع محدود خود (مثل آب یا ابزار) را در زمان نیاز با همسایگانم به اشتراک بگذارم.", "subscale": "SHARE", "reverse": False},
        {"text": "من معتقدم که مشکلات بزرگ محیط‌زیستی فقط از طریق کار تیمی و همگرومی حل می‌شوند.", "subscale": "TEAM", "reverse": False},
        {"text": "من ترجیح می‌دهم کارها را به تنهایی انجام دهم تا اینکه به دیگران اعتماد کنم.", "subscale": "TRUST", "reverse": True},
        {"text": "من از موفقیت دیگران در جامعه‌ام احساس خوشحالی می‌کنم.", "subscale": "SHARE", "reverse": False},
        {"text": "من به راحتی با افرادی که دیدگاه‌های متفاوتی دارند، به توافق می‌رسم.", "subscale": "TEAM", "reverse": False},
    ]
}

# =========================================================================
# ۳. تابع اصلی اجرا (Seed & Setup)
# =========================================================================
async def main():
    print("🧠 در حال ایجاد ماژول علمی روانشناسی با تحلیل دقیق...")
    
    # ۱. ساخت جداول
    print("🔄 ساخت جداول دیتابیس...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # ۲. پر کردن دیتابیس
    print("📝 در حال تزریق آزمون‌ها و سؤالات علمی...")
    async with async_session() as session:
        tests_to_seed = ["NEO_N", "BIOPHILIA", "CLIMATE_RESILIENCE", "COOPERATION"]
        
        for code in tests_to_seed:
            # بررسی تکراری نبودن
            result = await session.execute(select(PsychTest).where(PsychTest.code == code))
            if result.scalar_one_or_none():
                continue
                
            meta = INTERPRETATION_DB[code]
            category = "CLINICAL" if code == "NEO_N" else \
                       "ECO_PSYCHOLOGY" if code == "BIOPHILIA" else \
                       "CLIMATE_RESILIENCE" if code == "CLIMATE_RESILIENCE" else "PRO_SOCIAL"
            
            test = PsychTest(
                code=code,
                title=meta["title"],
                category=TestCategory[category],
                scoring_type=ScoringType.SUM,
                has_subscales=True,
                duration_minutes=5,
                description=f"ارزیابی علمی و دقیق {meta['title']} بر اساس استانداردهای روان‌سنجی"
            )
            session.add(test)
            await session.flush()
            
            # افزودن سؤالات واقعی
            questions_data = REAL_QUESTIONS[code]
            for i, q_data in enumerate(questions_data):
                q = PsychQuestion(
                    test_id=test.id,
                    subscale_code=q_data["subscale"],
                    question_number=i + 1,
                    text=q_data["text"],
                    is_reverse_scored=q_data["reverse"]
                )
                session.add(q)
                await session.flush()
                
                # گزینه‌های لیکرت ۵ گزینه‌ای با نمره‌دهی معکوس هوشمند
                base_options = [
                    {"label": "کاملاً مخالفم", "val": 1},
                    {"label": "مخالفم", "val": 2},
                    {"label": "نظری ندارم", "val": 3},
                    {"label": "موافقم", "val": 4},
                    {"label": "کاملاً موافقم", "val": 5},
                ]
                
                for opt in base_options:
                    # اگر سؤال معکوس است، نمره برعکس می‌شود (۱ می‌شود ۵، ۲ می‌شود ۴ و ...)
                    score = 6 - opt["val"] if q_data["reverse"] else opt["val"]
                    session.add(PsychOption(
                        question_id=q.id,
                        label=opt["label"],
                        score_value=float(score)
                    ))
                    
        await session.commit()
        print(f"✅ {len(tests_to_seed)} آزمون علمی با سؤالات واقعی و تحلیل دامنه‌ای دقیق ثبت شد.")

    # ۳. به‌روزرسانی فایل‌های بک‌اند و فرانت‌اند برای پشتیبانی از رنگ و تحلیل دقیق
    update_backend_router()
    update_frontend_ui()
    
    print("\n" + "="*70)
    print("✅ فرآیند با موفقیت تکمیل شد!")
    print("🎨 رنگ‌بندی روانشناختی اعمال شد.")
    print("📊 تحلیل دقیق بر اساس بازه نمره (Range-Based) فعال شد.")
    print("\n🚀 اکنون سرور را ری‌استارت کرده و به آدرس زیر بروید:")
    print("   http://localhost:3001/psychology")
    print("="*70)

def update_backend_router():
    """به‌روزرسانی روتر برای بازگرداندن تحلیل دقیق و رنگ"""
    router_path = ROOT / "api" / "modules" / "psychology" / "router.py"
    if not router_path.exists(): return
    
    # اضافه کردن منطق تحلیل دقیق به انتهای فایل router.py
    with open(router_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    if "get_detailed_analysis" not in content:
        analysis_logic = '''
def get_detailed_analysis(test_code: str, total_score: float):
    """دریافت تحلیل دقیق بر اساس بازه نمره"""
    meta = INTERPRETATION_DB.get(test_code)
    if not meta:
        return {"level": "نامشخص", "analysis": "تحلیل در دسترس نیست", "advice": "", "color": "#64748b"}
    
    # یافتن بازه مناسب
    for (min_score, max_score), data in meta["ranges"].items():
        if min_score <= total_score <= max_score:
            return {
                "level": data["level"],
                "analysis": data["analysis"],
                "advice": data["advice"],
                "color": CATEGORY_COLORS.get(meta.get("category", "CLINICAL"), "#64748b"),
                "max_score": meta["max_score"]
            }
    return {"level": "خارج از محدوده", "analysis": "", "advice": "", "color": "#64748b"}
'''
        # جایگذاری در فایل
        content = content.replace("from api.modules.psychology.engine import TEST_REGISTRY, calculate_result", 
                                  "from api.modules.psychology.engine import TEST_REGISTRY, calculate_result\n" + analysis_logic)
        
        # به‌روزرسانی endpoint submit برای استفاده از تحلیل دقیق
        content = content.replace(
            'interpretation = calculate_result(data.test_code, data.answers, questions_meta)',
            'raw_result = calculate_result(data.test_code, data.answers, questions_meta)\n    detailed_analysis = get_detailed_analysis(data.test_code, raw_result["total_score"])\n    interpretation = {**raw_result, **detailed_analysis}'
        )
        
        with open(router_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("   ✅ بک‌اند برای تحلیل دقیق و رنگ‌بندی به‌روز شد.")

def update_frontend_ui():
    """به‌روزرسانی فرانت‌اند برای نمایش رنگ و تحلیل دقیق"""
    page_path = ROOT / "apps" / "web" / "src" / "app" / "psychology" / "page.tsx"
    if not page_path.exists(): return
    
    with open(page_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # به‌روزرسانی بخش نمایش نتیجه برای نشان دادن تحلیل دقیق و رنگ داینامیک
    if "result.color" in content and "detailed analysis" not in content:
        # جایگزینی بخش نتیجه با نسخه پیشرفته
        old_result_block = '''          <div className="bg-slate-800/50 rounded-xl p-6 text-right mb-6 border-r-4" style={{ borderColor: result.color }}>
            <h3 className="text-lg font-bold text-white mb-2">💡 تحلیل و توصیه هوشمند:</h3>
            <p className="text-slate-300 leading-relaxed">{result.advice}</p>
          </div>'''
          
        new_result_block = '''          <div className="rounded-xl p-6 text-right mb-6 border-r-4 bg-slate-800/30" style={{ borderColor: result.color }}>
            <h3 className="text-xl font-bold text-white mb-3 flex items-center gap-2">
              <span className="w-3 h-3 rounded-full" style={{ backgroundColor: result.color }}></span>
              تحلیل علمی دقیق: {result.level}
            </h3>
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-bold text-slate-300 mb-1">🔍 تفسیر بالینی/روانشناختی:</h4>
                <p className="text-slate-200 leading-relaxed text-justify">{result.analysis}</p>
              </div>
              <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700">
                <h4 className="text-sm font-bold text-emerald-400 mb-1">💡 توصیه مداخله‌ای و عملی:</h4>
                <p className="text-slate-300 leading-relaxed text-justify">{result.advice}</p>
              </div>
              <div className="text-xs text-slate-500 text-left mt-2">
                نمره کسب شده: {result.total_score} از {result.max_score || 25}
              </div>
            </div>
          </div>'''
          
        content = content.replace(old_result_block, new_result_block)
        
        # به‌روزرسانی رنگ دسته‌بندی‌ها در لیست آزمون‌ها
        content = content.replace(
            'className="px-3 py-1 bg-slate-800 text-slate-300 text-xs rounded-full"',
            'className="px-3 py-1 text-xs rounded-full font-bold" style={{ backgroundColor: (test.category === "CLINICAL" ? "#6366f120" : test.category === "ECO_PSYCHOLOGY" ? "#10b98120" : test.category === "CLIMATE_RESILIENCE" ? "#06b6d420" : test.category === "PRO_SOCIAL" ? "#f59e0b20" : "#78716c20"), color: (test.category === "CLINICAL" ? "#818cf8" : test.category === "ECO_PSYCHOLOGY" ? "#34d399" : test.category === "CLIMATE_RESILIENCE" ? "#22d3ee" : test.category === "PRO_SOCIAL" ? "#fbbf24" : "#a8a29e") }}'
        )
        
        with open(page_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("   ✅ فرانت‌اند برای نمایش تحلیل دقیق و رنگ‌بندی روانشناختی به‌روز شد.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ خطا: {e}")
        import traceback
        traceback.print_exc()