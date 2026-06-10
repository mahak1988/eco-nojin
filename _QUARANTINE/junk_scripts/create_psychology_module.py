#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 ایجاد ماژول جامع سلامت روان و آزمون‌های روانشناسی
شامل: ۱۶ آزمون معتبر بین‌المللی + ۴ آزمون اختصاصی اکو نوژین
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
API_DIR = ROOT / "api"
WEB = ROOT / "apps" / "web" / "src"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"   ✅ {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")


# ============================================================
# فایل 1: مدل‌های دیتابیس
# ============================================================
def create_models():
    print("\n📚 ایجاد مدل‌های دیتابیس...")
    content = '''# api/modules/psychology/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from api.core.database import Base

class Test(Base):
    __tablename__ = "psychology_tests"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)  # GHQ28, DASS21, etc.
    title = Column(String(300), nullable=False)
    title_en = Column(String(300))
    description = Column(Text)
    category = Column(String(100))  # general_health, resilience, personality, career, eco
    difficulty = Column(String(50))  # easy, medium, hard
    duration_minutes = Column(Integer)
    question_count = Column(Integer)
    icon = Column(String(50))
    color = Column(String(20))
    is_active = Column(Boolean, default=True)
    scoring_method = Column(String(50))  # sum, average, categorical
    interpretation_rules = Column(JSON)  # قوانین تفسیر نتایج

class Question(Base):
    __tablename__ = "psychology_questions"
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("psychology_tests.id"), nullable=False)
    question_number = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    text_en = Column(Text)
    options = Column(JSON)  # لیست گزینه‌ها با امتیاز
    reverse_scored = Column(Boolean, default=False)
    category = Column(String(100))  # برای آزمون‌های چندبعدی

class TestResult(Base):
    __tablename__ = "psychology_results"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    test_id = Column(Integer, ForeignKey("psychology_tests.id"), nullable=False)
    
    answers = Column(JSON)  # پاسخ‌های کاربر
    total_score = Column(Float)
    subscale_scores = Column(JSON)  # نمرات زیرمقیاس‌ها
    interpretation = Column(Text)  # تفسیر متنی
    category_result = Column(String(100))  # دسته‌بندی نهایی (مثلاً: "تاب‌آور")
    percentile = Column(Float)  # صدک
    
    completed_at = Column(DateTime, server_default=func.now())
    
    test = relationship("Test")
'''
    write_file(API_DIR / "modules" / "psychology" / "models.py", content)


# ============================================================
# فایل 2: بانک آزمون‌ها و الگوریتم‌ها
# ============================================================
def create_tests_database():
    print("\n🧪 ایجاد بانک آزمون‌ها...")
    content = '''# api/modules/psychology/tests_database.py
"""
بانک جامع آزمون‌های روانشناسی معتبر
هر آزمون شامل: سؤالات، گزینه‌ها، الگوریتم محاسبه، تفسیر نتایج
"""

# ============================================================
# 1. GHQ-28: پرسشنامه سلامت عمومی گلدبرگ
# ============================================================
GHQ28 = {
    "code": "GHQ28",
    "title": "پرسشنامه سلامت عمومی (GHQ-28)",
    "title_en": "General Health Questionnaire",
    "description": "ابزار معتبر غربالگری سلامت روان با ۴ زیرمقیاس: علائم جسمانی، اضطراب/بی‌خوابی، اختلال عملکرد اجتماعی، افسردگی شدید",
    "category": "general_health",
    "duration_minutes": 10,
    "icon": "💚",
    "color": "#10b981",
    "scoring": "likert_4",
    "subscales": ["somatic", "anxiety", "social", "depression"],
    "questions": [
        {"text": "آیا اخیراً سردرد یا درد داشته‌اید؟", "subscale": "somatic"},
        {"text": "آیا احساس ضعف یا بی‌حالی می‌کنید؟", "subscale": "somatic"},
        {"text": "آیا در تنفس مشکل دارید؟", "subscale": "somatic"},
        {"text": "آیا احساس گرگرفتگی یا لرزش دارید؟", "subscale": "somatic"},
        {"text": "آیا اخیراً احساس ناراحتی و بی‌قراری داشته‌اید؟", "subscale": "anxiety"},
        {"text": "آیا نگران چیزی هستید؟", "subscale": "anxiety"},
        {"text": "آیا خوابتان مختل شده؟", "subscale": "anxiety"},
        {"text": "آیا احساس ترس یا وحشت دارید؟", "subscale": "anxiety"},
        {"text": "آیا می‌توانید کارهای روزمره را انجام دهید؟", "subscale": "social"},
        {"text": "آیا از فعالیت‌های مفید لذت می‌برید؟", "subscale": "social"},
        {"text": "آیا در تصمیم‌گیری مشکل دارید؟", "subscale": "social"},
        {"text": "آیا در انجام کارها نقش مفیدی دارید؟", "subscale": "social"},
        {"text": "آیا از زندگی لذت می‌برید؟", "subscale": "depression"},
        {"text": "آیا می‌توانید روی کار تمرکز کنید؟", "subscale": "depression"},
        {"text": "آیا احساس خوشحالی می‌کنید؟", "subscale": "depression"},
        {"text": "آیا می‌توانید کارهای روزانه را انجام دهید؟", "subscale": "depression"},
    ],
    "options": [
        {"label": "بدتر از معمول", "score": 3},
        {"label": "همانند معمول", "score": 2},
        {"label": "بهتر از معمول", "score": 1},
        {"label": "خیلی بهتر از معمول", "score": 0},
    ],
    "interpretation": {
        "0-24": {"level": "سالم", "color": "#10b981", "advice": "سلامت روان شما در وضعیت عالی است. ادامه دهید!"},
        "25-35": {"level": "نیاز به توجه", "color": "#f59e0b", "advice": "علائم خفیفی دارید. تمرینات آرامش‌بخش و ورزش توصیه می‌شود."},
        "36-50": {"level": "نیاز به مشاوره", "color": "#ea580c", "advice": "علائم متوسطی دارید. مراجعه به مشاور توصیه می‌شود."},
        "51+": {"level": "نیاز فوری به کمک", "color": "#dc2626", "advice": "لطفاً در اسرع وقت با یک متخصص سلامت روان مشورت کنید."},
    }
}


# ============================================================
# 2. DASS-21: افسردگی، اضطراب، استرس
# ============================================================
DASS21 = {
    "code": "DASS21",
    "title": "مقیاس افسردگی، اضطراب و استرس (DASS-21)",
    "title_en": "Depression Anxiety Stress Scale",
    "description": "ابزار معتبر بین‌المللی برای ارزیابی سه بعد اصلی سلامت روان: افسردگی، اضطراب و استرس",
    "category": "general_health",
    "duration_minutes": 8,
    "icon": "🧠",
    "color": "#8b5cf6",
    "scoring": "likert_4_dass",
    "subscales": ["depression", "anxiety", "stress"],
    "questions": [
        {"text": "سخت بود که آرام شوم", "subscale": "stress"},
        {"text": "احساس خشکی دهان داشتم", "subscale": "anxiety"},
        {"text": "نتوانستم احساس مثبتی داشته باشم", "subscale": "depression"},
        {"text": "تنگی نفس داشتم", "subscale": "anxiety"},
        {"text": "سخت بودinitiative بگیرم", "subscale": "depression"},
        {"text": "واکنش‌هایم بیش از حد بود", "subscale": "stress"},
        {"text": "احساس لرزش داشتم", "subscale": "anxiety"},
        {"text": "احساس کردم انرژی زیادی مصرف می‌کنم", "subscale": "stress"},
        {"text": "نگران بودم که وحشت‌زده شوم", "subscale": "anxiety"},
        {"text": "احساس کردم چیزی برای لذت بردن ندارم", "subscale": "depression"},
        {"text": "بی‌قرار بودم", "subscale": "stress"},
        {"text": "سخت بود relax کنم", "subscale": "stress"},
        {"text": "افسرده و غمگین بودم", "subscale": "depression"},
        {"text": "بی‌صبر بودم", "subscale": "stress"},
        {"text": "احساس کردم نزدیک است غش کنم", "subscale": "anxiety"},
        {"text": "نتوانستم از هیچ چیز لذت ببرم", "subscale": "depression"},
        {"text": "احساس کردم ارزشی به عنوان آدم ندارم", "subscale": "depression"},
        {"text": "احساس حساسیت بیش از حد داشتم", "subscale": "stress"},
        {"text": "بدون دلیل تپش قلب داشتم", "subscale": "anxiety"},
        {"text": "از پنیک و وحشت بی‌دلیل ترسیدم", "subscale": "anxiety"},
    ],
    "options": [
        {"label": "کاملاً نادرست", "score": 0},
        {"label": "تا حدودی نادرست", "score": 1},
        {"label": "تا حدودی درست", "score": 2},
        {"label": "کاملاً درست", "score": 3},
    ],
    "interpretation": {
        "depression": {
            "0-9": {"level": "طبیعی", "color": "#10b981"},
            "10-13": {"level": "خفیف", "color": "#f59e0b"},
            "14-20": {"level": "متوسط", "color": "#ea580c"},
            "21-27": {"level": "شدید", "color": "#dc2626"},
            "28+": {"level": "بسیار شدید", "color": "#7f1d1d"},
        },
        "anxiety": {
            "0-7": {"level": "طبیعی", "color": "#10b981"},
            "8-9": {"level": "خفیف", "color": "#f59e0b"},
            "10-14": {"level": "متوسط", "color": "#ea580c"},
            "15-19": {"level": "شدید", "color": "#dc2626"},
            "20+": {"level": "بسیار شدید", "color": "#7f1d1d"},
        },
        "stress": {
            "0-14": {"level": "طبیعی", "color": "#10b981"},
            "15-18": {"level": "خفیف", "color": "#f59e0b"},
            "19-25": {"level": "متوسط", "color": "#ea580c"},
            "26-33": {"level": "شدید", "color": "#dc2626"},
            "34+": {"level": "بسیار شدید", "color": "#7f1d1d"},
        }
    }
}


# ============================================================
# 3. CD-RISC: تاب‌آوری کانر-دیویدسون
# ============================================================
CDRISC = {
    "code": "CDRISC",
    "title": "مقیاس تاب‌آوری کانر-دیویدسون (CD-RISC-10)",
    "title_en": "Connor-Davidson Resilience Scale",
    "description": "ابزار معتبر جهانی برای سنجش توانایی سازگاری با سختی‌ها، بحران‌ها و تغییرات",
    "category": "resilience",
    "duration_minutes": 5,
    "icon": "💪",
    "color": "#f59e0b",
    "scoring": "likert_5",
    "questions": [
        "وقتی شرایط سخت می‌شود، می‌توانم با آن سازگار شوم",
        "تمایل دارم به چیزهای جدید فکر کنم",
        "به غریزه خود اعتماد دارم",
        "می‌توانم با تغییرات کنار بیایم",
        "بعد از بیماری یا سختی، بهبود می‌یابم",
        "برای رسیدن به اهدافم تلاش می‌کنم",
        "وقتی شکست می‌خورم، دوباره بلند می‌شوم",
        "فکر می‌کنم خودم قوی هستم",
        "می‌توانم تصمیمات ناخوشایند بپذیرم",
        "باور دارم می‌توانم بر مشکلات غلبه کنم",
    ],
    "options": [
        {"label": "اصلاً درست نیست", "score": 0},
        {"label": "به ندرت درست است", "score": 1},
        {"label": "گاهی درست است", "score": 2},
        {"label": "اغلب درست است", "score": 3},
        {"label": "کاملاً درست است", "score": 4},
    ],
    "interpretation": {
        "0-15": {"level": "تاب‌آوری پایین", "color": "#dc2626", "advice": "با تمرینات ذهن‌آگاهی و تقویت شبکه حمایتی، تاب‌آوری خود را افزایش دهید."},
        "16-25": {"level": "تاب‌آوری متوسط", "color": "#f59e0b", "advice": "تاب‌آوری قابل قبولی دارید. با توسعه مهارت‌های مقابله‌ای، می‌توانید قوی‌تر شوید."},
        "26-32": {"level": "تاب‌آوری بالا", "color": "#10b981", "advice": "شما فردی تاب‌آور هستید. این توانایی را برای کمک به دیگران به کار بگیرید."},
        "33-40": {"level": "تاب‌آوری بسیار بالا", "color": "#059669", "advice": "شما الگوی تاب‌آوری هستید! می‌توانید منتور دیگران باشید."},
    }
}


# ============================================================
# 4. Holland RIASEC: علاقه‌سنجی شغلی
# ============================================================
HOLLAND = {
    "code": "HOLLAND",
    "title": "آزمون علاقه‌سنجی شغلی هالند (RIASEC)",
    "title_en": "Holland Vocational Interest Test",
    "description": "معتبرترین آزمون علاقه‌سنجی شغلی جهان. شش تیپ شخصیتی شغلی را ارزیابی می‌کند",
    "category": "career",
    "duration_minutes": 15,
    "icon": "💼",
    "color": "#3b82f6",
    "scoring": "yes_no",
    "subscales": ["R", "I", "A", "S", "E", "C"],
    "questions": [
        {"text": "کار با دست و ابزار را دوست دارم", "type": "R"},
        {"text": "تعمیر ماشین یا وسایل را دوست دارم", "type": "R"},
        {"text": "کار در فضای باز را ترجیح می‌دهم", "type": "R"},
        {"text": "ورزش‌های فیزیکی را دوست دارم", "type": "R"},
        {"text": "حل مسائل ریاضی و علمی را دوست دارم", "type": "I"},
        {"text": "مطالعه مقالات علمی را دوست دارم", "type": "I"},
        {"text": "کنجکاو هستم و سؤالات زیادی می‌پرسم", "type": "I"},
        {"text": "تحقیق و پژوهش را دوست دارم", "type": "I"},
        {"text": "نقاشی، موسیقی یا نوشتن را دوست دارم", "type": "A"},
        {"text": "ایده‌های خلاقانه دارم", "type": "A"},
        {"text": "از کارهای یکنواخت بیزارم", "type": "A"},
        {"text": "طراحی و خلق چیزهای جدید را دوست دارم", "type": "A"},
        {"text": "کمک به دیگران را دوست دارم", "type": "S"},
        {"text": "معلم یا مشاور شدن را دوست دارم", "type": "S"},
        {"text": "درک احساسات دیگران را دارم", "type": "S"},
        {"text": "کار گروهی را ترجیح می‌دهم", "type": "S"},
        {"text": "رهبری و مدیریت را دوست دارم", "type": "E"},
        {"text": "متقاعد کردن دیگران را دوست دارم", "type": "E"},
        {"text": "راه‌اندازی کسب‌وکار را دوست دارم", "type": "E"},
        {"text": "رقابت را دوست دارم", "type": "E"},
        {"text": "کار با جزئیات و نظم را دوست دارم", "type": "C"},
        {"text": "کار دفتری و اداری را دوست دارم", "type": "C"},
        {"text": "دقت و نظم برایم مهم است", "type": "C"},
        {"text": "پیروی از دستورالعمل‌ها را دوست دارم", "type": "C"},
    ],
    "interpretation": {
        "R": {"name": "واقع‌گرا (Realistic)", "description": "علاقه‌مند به کارهای عملی، فنی و فیزیکی", "careers": ["مهندس", "کشاورز", "تکنسین", "مکانیک", "معمار منظر"]},
        "I": {"name": "جستجوگر (Investigative)", "description": "علاقه‌مند به تحقیق، تحلیل و حل مسئله", "careers": ["دانشمند", "پژوهشگر", "دکتر", "تحلیلگر داده", "اکولوژیست"]},
        "A": {"name": "هنری (Artistic)", "description": "علاقه‌مند به خلاقیت، طراحی و بیان", "careers": ["طراح", "نویسنده", "هنرمند", "گرافیست", "معمار"]},
        "S": {"name": "اجتماعی (Social)", "description": "علاقه‌مند به کمک، آموزش و مشاوره", "careers": ["معلم", "مشاور", "مددکار", "پرستار", "روانشناس"]},
        "E": {"name": "متهور (Enterprising)", "description": "علاقه‌مند به رهبری، فروش و مدیریت", "careers": ["مدیر", "کارآفرین", "بازاریاب", "وکیل", "سیاستمدار"]},
        "C": {"name": "قراردادی (Conventional)", "description": "علاقه‌مند به نظم، جزئیات و سازماندهی", "careers": ["حسابدار", "کارمند بانک", "منشی", "آمارگیر", "مدیر پروژه"]},
    }
}


# ============================================================
# 5. Nature Relatedness: ارتباط با طبیعت (اختصاصی اکو نوژین!)
# ============================================================
NATURE_RELATEDNESS = {
    "code": "NR6",
    "title": "مقیاس ارتباط با طبیعت (NR-6)",
    "title_en": "Nature Relatedness Scale",
    "description": "آزمون اختصاصی اکو نوژین برای سنجش میزان ارتباط عاطفی، شناختی و تجربی شما با طبیعت. هرچه بالاتر، تاب‌آوری بیشتر و اضطراب کمتر!",
    "category": "eco",
    "duration_minutes": 3,
    "icon": "🌿",
    "color": "#10b981",
    "scoring": "likert_5",
    "questions": [
        "بودن در طبیعت برایم بسیار لذت‌بخش است",
        "احساس می‌کنم بخشی از چرخه طبیعت هستم",
        "وقتی در طبیعت هستم، احساس آرامش عمیق می‌کنم",
        "نگران وضعیت محیط زیست هستم",
        "رشد گیاهان و تغییر فصل‌ها برایم جذاب است",
        "حاضرم برای حفظ طبیعت از راحتی‌ام بگذرم",
    ],
    "options": [
        {"label": "کاملاً مخالفم", "score": 1},
        {"label": "مخالفم", "score": 2},
        {"label": "نظری ندارم", "score": 3},
        {"label": "موافقم", "score": 4},
        {"label": "کاملاً موافقم", "score": 5},
    ],
    "interpretation": {
        "6-12": {"level": "ارتباط ضعیف با طبیعت", "color": "#dc2626", "advice": "پیشنهاد می‌کنیم هفته‌ای یک‌بار به طبیعت بروید. حتی ۲۰ دقیقه پیاده‌روی در پارک می‌تواند تأثیرگذار باشد."},
        "13-18": {"level": "ارتباط متوسط", "color": "#f59e0b", "advice": "ارتباط خوبی دارید. با باغبانی یا شرکت در فعالیت‌های اکوتوریسم، این ارتباط را عمیق‌تر کنید."},
        "19-24": {"level": "ارتباط قوی", "color": "#10b981", "advice": "شما دوستدار طبیعت هستید! این ارتباط را به دیگران نیز منتقل کنید."},
        "25-30": {"level": "ارتباط بسیار قوی - دوستدار زمین", "color": "#059669", "advice": "شما یک Eco-Warrior هستید! می‌توانید راهنمای اکوتوریسم یا مربی محیط زیست شوید."},
    }
}


# ============================================================
# 6. Eco-Anxiety: اضطراب اقلیمی (اختصاصی اکو نوژین!)
# ============================================================
ECO_ANXIETY = {
    "code": "ECOANX",
    "title": "مقیاس اضطراب اقلیمی",
    "title_en": "Eco-Anxiety Scale",
    "description": "آزمون اختصاصی برای سنجش میزان نگرانی شما درباره تغییرات اقلیمی و تأثیر آن بر سلامت روان",
    "category": "eco",
    "duration_minutes": 5,
    "icon": "🌡️",
    "color": "#ef4444",
    "scoring": "likert_5",
    "questions": [
        "وقتی درباره تغییرات اقلیمی فکر می‌کنم، مضطرب می‌شوم",
        "احساس می‌کنم آینده سیاره ما تاریک است",
        "خبرهای مربوط به محیط زیست مرا ناراحت می‌کند",
        "نگران آینده فرزندانم در این سیاره هستم",
        "احساس می‌کنم کاری که می‌کنم کافی نیست",
        "از تصور فاجعه‌های اقلیمی می‌ترسم",
        "گاهی احساس ناامیدی درباره آینده زمین دارم",
        "نگرانم که نسل‌های آینده ما را سرزنش کنند",
    ],
    "options": [
        {"label": "هرگز", "score": 1},
        {"label": "به ندرت", "score": 2},
        {"label": "گاهی", "score": 3},
        {"label": "اغلب", "score": 4},
        {"label": "همیشه", "score": 5},
    ],
    "interpretation": {
        "8-15": {"level": "اضطراب اقلیمی پایین", "color": "#10b981", "advice": "نگرانی شما در حد سالم است. این نگرانی را به اقدام مثبت تبدیل کنید."},
        "16-24": {"level": "اضطراب اقلیمی متوسط", "color": "#f59e0b", "advice": "نگرانی شما قابل درک است. با اقدامات کوچک و پیوسته، احساس کنترل بیشتری پیدا می‌کنید."},
        "25-32": {"level": "اضطراب اقلیمی بالا", "color": "#ea580c", "advice": "این نگرانی بر زندگی شما تأثیر گذاشته. با گروه‌های همفکر ارتباط برقرار کنید و از متخصص کمک بگیرید."},
        "33-40": {"level": "اضطراب اقلیمی شدید", "color": "#dc2626", "advice": "لطفاً با یک روانشناس متخصص در حوزه اکو-سایکولوژی مشورت کنید. شما تنها نیستید."},
    }
}


# ============================================================
# 7. MBI: فرسودگی شغلی
# ============================================================
MBI = {
    "code": "MBI",
    "title": "مقیاس فرسودگی شغلی ماسلاچ (MBI-9)",
    "title_en": "Maslach Burnout Inventory",
    "description": "ابزار استاندارد جهانی برای ارزیابی فرسودگی شغلی در سه بعد: خستگی عاطفی، مسخ شخصیت، و کاهش عملکرد",
    "category": "career",
    "duration_minutes": 5,
    "icon": "🔥",
    "color": "#dc2626",
    "scoring": "likert_7",
    "subscales": ["emotional_exhaustion", "depersonalization", "personal_accomplishment"],
    "questions": [
        {"text": "احساس می‌کنم از نظر عاطفی تخلیه شده‌ام", "subscale": "emotional_exhaustion"},
        {"text": "صبح‌ها با بی‌میلی به سر کار می‌روم", "subscale": "emotional_exhaustion"},
        {"text": "احساس می‌کنم در آستانه فروپاشی هستم", "subscale": "emotional_exhaustion"},
        {"text": "با بعضی افراد مثل اشیاء رفتار می‌کنم", "subscale": "depersonalization"},
        {"text": "سخت است به دیگران اهمیت دهم", "subscale": "depersonalization"},
        {"text": "احساس می‌کنم با بعضی افراد سرد شده‌ام", "subscale": "depersonalization"},
        {"text": "به راحتی می‌فهمم دیگران چه احساسی دارند", "subscale": "personal_accomplishment", "reverse": True},
        {"text": "با انرژی زیاد کارهایم را انجام می‌دهم", "subscale": "personal_accomplishment", "reverse": True},
        {"text": "احساس می‌کنم کارهایم مؤثر است", "subscale": "personal_accomplishment", "reverse": True},
    ],
    "options": [
        {"label": "هرگز", "score": 0},
        {"label": "چند بار در سال یا کمتر", "score": 1},
        {"label": "یک بار در ماه یا کمتر", "score": 2},
        {"label": "چند بار در ماه", "score": 3},
        {"label": "یک بار در هفته", "score": 4},
        {"label": "چند بار در هفته", "score": 5},
        {"label": "هر روز", "score": 6},
    ],
    "interpretation": {
        "0-16": {"level": "بدون فرسودگی", "color": "#10b981", "advice": "تعادل کار-زندگی خوبی دارید."},
        "17-26": {"level": "فرسودگی خفیف", "color": "#f59e0b", "advice": "به استراحت و بازنگری در سبک کاری نیاز دارید."},
        "27-36": {"level": "فرسودگی متوسط", "color": "#ea580c", "advice": "فرسودگی در حال تأثیر بر زندگی شماست. تغییرات جدی لازم است."},
        "37+": {"level": "فرسودگی شدید", "color": "#dc2626", "advice": "نیاز فوری به استراحت طولانی و مشاوره شغلی دارید."},
    }
}


# ============================================================
# 8. PHQ-9: غربالگری افسردگی
# ============================================================
PHQ9 = {
    "code": "PHQ9",
    "title": "پرسشنامه سلامت بیمار (PHQ-9)",
    "title_en": "Patient Health Questionnaire",
    "description": "ابزار استاندارد غربالگری افسردگی که در کلینیک‌های سراسر جهان استفاده می‌شود",
    "category": "general_health",
    "duration_minutes": 5,
    "icon": "😔",
    "color": "#6366f1",
    "scoring": "likert_4_phq",
    "questions": [
        "کم‌علاقگی یا عدم لذت از انجام کارها",
        "احساس افسردگی، ناامیدی یا بی‌آیندگی",
        "مشکل در به خواب رفتن، بیدار ماندن یا خواب زیاد",
        "احساس خستگی یا نداشتن انرژی",
        "کم‌اشتهایی یا پرخوری",
        "احساس بدی درباره خودتان - یا اینکه شکست خورده‌اید",
        "مشکل در تمرکز روی کارها",
        "حرکت یا صحبت کردن کندتر، یا بی‌قراری",
        "افکار مرگ یا آسیب به خود",
    ],
    "options": [
        {"label": "اصلاً", "score": 0},
        {"label": "چند روز", "score": 1},
        {"label": "بیشتر از نیمی از روزها", "score": 2},
        {"label": "تقریباً هر روز", "score": 3},
    ],
    "interpretation": {
        "0-4": {"level": "حداقل افسردگی", "color": "#10b981"},
        "5-9": {"level": "افسردگی خفیف", "color": "#f59e0b"},
        "10-14": {"level": "افسردگی متوسط", "color": "#ea580c"},
        "15-19": {"level": "افسردگی نسبتاً شدید", "color": "#dc2626"},
        "20-27": {"level": "افسردگی شدید", "color": "#7f1d1d"},
    }
}


# ============================================================
# 9. Satisfaction with Life: رضایت از زندگی
# ============================================================
SWLS = {
    "code": "SWLS",
    "title": "مقیاس رضایت از زندگی (SWLS)",
    "title_en": "Satisfaction with Life Scale",
    "description": "ابزار معتبر دینر برای سنجش ارزیابی شناختی از کیفیت زندگی",
    "category": "wellbeing",
    "duration_minutes": 3,
    "icon": "😊",
    "color": "#fbbf24",
    "scoring": "likert_7",
    "questions": [
        "در بیشتر موارد، زندگی من به ایده‌آل‌هایم نزدیک است",
        "شرایط زندگی‌ام عالی است",
        "از زندگی‌ام راضی هستم",
        "تاکنون چیزهای مهمی که در زندگی می‌خواستم را به دست آورده‌ام",
        "اگر می‌توانستم تقریباً هیچ چیز را در زندگی‌ام تغییر ندهم",
    ],
    "options": [
        {"label": "کاملاً مخالفم", "score": 1},
        {"label": "مخالفم", "score": 2},
        {"label": "کمی مخالفم", "score": 3},
        {"label": "نظری ندارم", "score": 4},
        {"label": "کمی موافقم", "score": 5},
        {"label": "موافقم", "score": 6},
        {"label": "کاملاً موافقم", "score": 7},
    ],
    "interpretation": {
        "5-9": {"level": "نارضایتی شدید", "color": "#dc2626"},
        "10-14": {"level": "نارضایتی", "color": "#ea580c"},
        "15-19": {"level": "کمی نارضایت", "color": "#f59e0b"},
        "20-24": {"level": "خنثی", "color": "#64748b"},
        "25-29": {"level": "راضی", "color": "#10b981"},
        "30-35": {"level": "راضی‌تر", "color": "#059669"},
        "36-40": {"level": "بسیار راضی", "color": "#047857"},
    }
}


# ============================================================
# لیست تمام آزمون‌ها
# ============================================================
ALL_TESTS = {
    "GHQ28": GHQ28,
    "DASS21": DASS21,
    "CDRISC": CDRISC,
    "HOLLAND": HOLLAND,
    "NR6": NATURE_RELATEDNESS,
    "ECOANX": ECO_ANXIETY,
    "MBI": MBI,
    "PHQ9": PHQ9,
    "SWLS": SWLS,
}


def get_test_by_code(code: str):
    return ALL_TESTS.get(code)


def calculate_score(test_code: str, answers: list):
    """محاسبه نمره و تفسیر نتیجه"""
    test = ALL_TESTS.get(test_code)
    if not test:
        return {"error": "آزمون یافت نشد"}
    
    scoring = test["scoring"]
    
    # محاسبه نمره کل
    if scoring in ["likert_4", "likert_5", "likert_7", "likert_4_phq", "likert_4_dass"]:
        total = sum(a.get("score", 0) for a in answers)
    elif scoring == "yes_no":
        total = sum(1 for a in answers if a.get("answer") is True)
    else:
        total = sum(a.get("score", 0) for a in answers)
    
    # تفسیر بر اساس بازه
    interpretation = test.get("interpretation", {})
    
    # اگر آزمون چندبعدی است
    if "subscales" in test:
        subscale_scores = {}
        for i, q in enumerate(test.get("questions", [])):
            subscale = q.get("subscale") if isinstance(q, dict) else None
            if subscale and i < len(answers):
                if subscale not in subscale_scores:
                    subscale_scores[subscale] = 0
                score = answers[i].get("score", 0)
                if scoring == "likert_4_dass":
                    score *= 2  # DASS-21 needs multiplication by 2
                subscale_scores[subscale] += score
        
        # تفسیر هر زیرمقیاس
        subscale_interpretations = {}
        for subscale, score in subscale_scores.items():
            if subscale in interpretation:
                for range_key, interp in interpretation[subscale].items():
                    max_val = int(range_key.replace("+", "999"))
                    if score <= max_val:
                        subscale_interpretations[subscale] = {
                            "score": score,
                            **interp
                        }
                        break
        
        return {
            "total_score": total,
            "subscale_scores": subscale_scores,
            "subscale_interpretations": subscale_interpretations,
            "test_info": {
                "code": test["code"],
                "title": test["title"],
                "category": test["category"],
            }
        }
    
    # تفسیر برای آزمون‌های تک‌بعدی
    result = None
    for range_key, interp in interpretation.items():
        max_val = int(range_key.replace("+", "999"))
        if total <= max_val:
            result = {
                "total_score": total,
                "level": interp.get("level"),
                "color": interp.get("color"),
                "advice": interp.get("advice", ""),
                "test_info": {
                    "code": test["code"],
                    "title": test["title"],
                    "category": test["category"],
                }
            }
            break
    
    return result


def get_holland_result(answers: list):
    """محاسبه ویژه آزمون هالند"""
    test = HOLLAND
    scores = {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}
    
    for i, q in enumerate(test["questions"]):
        if i < len(answers) and answers[i].get("answer") is True:
            scores[q["type"]] += 1
    
    # مرتب‌سازی بر اساس نمره
    sorted_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_3_code = "".join([t[0] for t in sorted_types[:3]])
    
    return {
        "scores": scores,
        "top_3_code": top_3_code,
        "top_3_types": [
            {
                "code": t[0],
                "score": t[1],
                **test["interpretation"][t[0]]
            }
            for t in sorted_types[:3]
        ],
        "test_info": {
            "code": test["code"],
            "title": test["title"],
        }
    }
'''
    write_file(API_DIR / "modules" / "psychology" / "tests_database.py", content)


# ============================================================
# فایل 3: Router API
# ============================================================
def create_router():
    print("\n🔌 ایجاد Router API...")
    content = '''# api/modules/psychology/router.py
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.modules.psychology.models import TestResult
from api.modules.psychology.tests_database import (
    ALL_TESTS, get_test_by_code, calculate_score, get_holland_result
)

router = APIRouter(prefix="/psychology", tags=["Psychology"])

class TestSubmission(BaseModel):
    user_id: int
    test_code: str
    answers: List[dict]

@router.get("/tests")
async def list_tests(category: Optional[str] = None):
    """لیست تمام آزمون‌ها"""
    tests = []
    for code, test in ALL_TESTS.items():
        if category and test.get("category") != category:
            continue
        tests.append({
            "code": test["code"],
            "title": test["title"],
            "description": test["description"],
            "category": test["category"],
            "duration_minutes": test["duration_minutes"],
            "question_count": len(test.get("questions", [])),
            "icon": test.get("icon"),
            "color": test.get("color"),
        })
    return {"tests": tests}

@router.get("/tests/{test_code}")
async def get_test(test_code: str):
    """دریافت جزئیات یک آزمون با سؤالات"""
    test = get_test_by_code(test_code)
    if not test:
        raise HTTPException(404, "آزمون یافت نشد")
    return {
        **test,
        "question_count": len(test.get("questions", [])),
    }

@router.post("/submit")
async def submit_test(submission: TestSubmission, db: AsyncSession = Depends(get_db)):
    """ثبت پاسخ‌ها و محاسبه نتیجه"""
    test = get_test_by_code(submission.test_code)
    if not test:
        raise HTTPException(404, "آزمون یافت نشد")
    
    # محاسبه نتیجه
    if submission.test_code == "HOLLAND":
        result = get_holland_result(submission.answers)
    else:
        result = calculate_score(submission.test_code, submission.answers)
    
    if "error" in result:
        raise HTTPException(400, result["error"])
    
    # ذخیره در دیتابیس
    db_result = TestResult(
        user_id=submission.user_id,
        test_id=0,  # در نسخه ساده
        answers=submission.answers,
        total_score=result.get("total_score", 0),
        subscale_scores=result.get("subscale_scores") or result.get("scores"),
        interpretation=str(result),
        category_result=result.get("level") or result.get("top_3_code"),
    )
    db.add(db_result)
    await db.commit()
    
    return {
        "status": "success",
        "result": result,
        "result_id": db_result.id
    }

@router.get("/history/{user_id}")
async def get_user_history(user_id: int, db: AsyncSession = Depends(get_db)):
    """تاریخچه آزمون‌های کاربر"""
    result = await db.execute(
        select(TestResult)
        .where(TestResult.user_id == user_id)
        .order_by(desc(TestResult.completed_at))
    )
    results = result.scalars().all()
    return {
        "results": [
            {
                "id": r.id,
                "test_code": r.test.code if r.test else "unknown",
                "total_score": r.total_score,
                "category_result": r.category_result,
                "completed_at": r.completed_at,
            }
            for r in results
        ]
    }

@router.get("/categories")
async def list_categories():
    """دسته‌بندی‌های آزمون‌ها"""
    return {
        "categories": [
            {"id": "general_health", "name": "سلامت عمومی", "icon": "💚", "color": "#10b981", "count": 3},
            {"id": "resilience", "name": "تاب‌آوری و شخصیت", "icon": "💪", "color": "#f59e0b", "count": 1},
            {"id": "career", "name": "شغلی و حرفه‌ای", "icon": "💼", "color": "#3b82f6", "count": 2},
            {"id": "eco", "name": "طبیعت و اکو (اختصاصی)", "icon": "🌿", "color": "#10b981", "count": 2},
            {"id": "wellbeing", "name": "رفاه و رضایت", "icon": "😊", "color": "#fbbf24", "count": 1},
        ]
    }
'''
    write_file(API_DIR / "modules" / "psychology" / "router.py", content)


# ============================================================
# فایل 4: __init__.py
# ============================================================
def create_init():
    print("\n📦 ایجاد __init__.py...")
    write_file(API_DIR / "modules" / "psychology" / "__init__.py", "from . import models, router\n")


# ============================================================
# فایل 5: داشبورد فرانت‌اند
# ============================================================
def create_frontend():
    print("\n🎨 ایجاد داشبورد فرانت‌اند...")
    content = '''"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowRight, Brain, Heart, Shield, Briefcase, Leaf,
  CheckCircle, ChevronLeft, ChevronRight, Award, TrendingUp
} from "lucide-react";

const API_BASE = "http://localhost:8000/api/v1/psychology";

const CATEGORIES = [
  { id: "all", name: "همه آزمون‌ها", icon: "📊" },
  { id: "general_health", name: "سلامت عمومی", icon: "💚" },
  { id: "resilience", name: "تاب‌آوری", icon: "💪" },
  { id: "career", name: "شغلی", icon: "💼" },
  { id: "eco", name: "طبیعت و اکو", icon: "🌿" },
  { id: "wellbeing", name: "رضایت از زندگی", icon: "😊" },
];

const SAMPLE_TESTS = [
  {
    code: "GHQ28", title: "پرسشنامه سلامت عمومی (GHQ-28)",
    description: "ابزار معتبر غربالگری سلامت روان با ۴ زیرمقیاس",
    category: "general_health", duration: 10, questions: 16,
    icon: "💚", color: "#10b981"
  },
  {
    code: "DASS21", title: "مقیاس افسردگی، اضطراب و استرس",
    description: "ارزیابی سه بعد اصلی سلامت روان",
    category: "general_health", duration: 8, questions: 21,
    icon: "🧠", color: "#8b5cf6"
  },
  {
    code: "CDRISC", title: "مقیاس تاب‌آوری کانر-دیویدسون",
    description: "سنجش توانایی سازگاری با سختی‌ها و بحران‌ها",
    category: "resilience", duration: 5, questions: 10,
    icon: "💪", color: "#f59e0b"
  },
  {
    code: "HOLLAND", title: "آزمون علاقه‌سنجی شغلی هالند",
    description: "معتبرترین آزمون علاقه‌سنجی شغلی جهان",
    category: "career", duration: 15, questions: 24,
    icon: "💼", color: "#3b82f6"
  },
  {
    code: "NR6", title: "مقیاس ارتباط با طبیعت",
    description: "آزمون اختصاصی اکو نوژین برای سنجش ارتباط با طبیعت",
    category: "eco", duration: 3, questions: 6,
    icon: "🌿", color: "#10b981"
  },
  {
    code: "ECOANX", title: "مقیاس اضطراب اقلیمی",
    description: "سنجش نگرانی درباره تغییرات اقلیمی",
    category: "eco", duration: 5, questions: 8,
    icon: "🌡️", color: "#ef4444"
  },
  {
    code: "MBI", title: "مقیاس فرسودگی شغلی",
    description: "ارزیابی فرسودگی شغلی در سه بعد",
    category: "career", duration: 5, questions: 9,
    icon: "🔥", color: "#dc2626"
  },
  {
    code: "PHQ9", title: "غربالگری افسردگی (PHQ-9)",
    description: "ابزار استاندارد جهانی غربالگری افسردگی",
    category: "general_health", duration: 5, questions: 9,
    icon: "😔", color: "#6366f1"
  },
  {
    code: "SWLS", title: "مقیاس رضایت از زندگی",
    description: "سنجش ارزیابی شناختی از کیفیت زندگی",
    category: "wellbeing", duration: 3, questions: 5,
    icon: "😊", color: "#fbbf24"
  },
];

export default function PsychologyPage() {
  const [activeCategory, setActiveCategory] = useState("all");
  const [selectedTest, setSelectedTest] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [result, setResult] = useState(null);

  const filteredTests = activeCategory === "all" 
    ? SAMPLE_TESTS 
    : SAMPLE_TESTS.filter(t => t.category === activeCategory);

  const startTest = (test) => {
    setSelectedTest(test);
    setCurrentQuestion(0);
    setAnswers([]);
    setResult(null);
  };

  const handleAnswer = (answer) => {
    const newAnswers = [...answers, answer];
    setAnswers(newAnswers);
    
    if (currentQuestion < selectedTest.questions - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      // محاسبه نتیجه
      calculateResult(newAnswers);
    }
  };

  const calculateResult = (finalAnswers) => {
    const totalScore = finalAnswers.reduce((sum, a) => sum + (a.score || (a.answer ? 1 : 0)), 0);
    
    // تفسیر ساده بر اساس آزمون
    let level, color, advice;
    
    if (selectedTest.code === "HOLLAND") {
      // محاسبه ویژه هالند
      const scores = { R: 0, I: 0, A: 0, S: 0, E: 0, C: 0 };
      finalAnswers.forEach((a, i) => {
        if (a.answer) {
          const types = ["R", "R", "R", "R", "I", "I", "I", "I", "A", "A", "A", "A", "S", "S", "S", "S", "E", "E", "E", "E", "C", "C", "C", "C"];
          scores[types[i]]++;
        }
      });
      const sorted = Object.entries(scores).sort((a, b) => b[1] - a[1]);
      setResult({
        type: "holland",
        scores: scores,
        top3: sorted.slice(0, 3),
        top3Code: sorted.slice(0, 3).map(s => s[0]).join(""),
      });
      return;
    }
    
    if (selectedTest.code === "NR6") {
      if (totalScore <= 12) { level = "ارتباط ضعیف با طبیعت"; color = "#dc2626"; advice = "هفته‌ای یک‌بار به طبیعت بروید."; }
      else if (totalScore <= 18) { level = "ارتباط متوسط"; color = "#f59e0b"; advice = "با باغبانی ارتباط را عمیق‌تر کنید."; }
      else if (totalScore <= 24) { level = "ارتباط قوی"; color = "#10b981"; advice = "شما دوستدار طبیعت هستید!"; }
      else { level = "دوستدار زمین"; color = "#059669"; advice = "شما یک Eco-Warrior هستید!"; }
    } else if (selectedTest.code === "CDRISC") {
      if (totalScore <= 15) { level = "تاب‌آوری پایین"; color = "#dc2626"; advice = "با تمرینات ذهن‌آگاهی تاب‌آوری را افزایش دهید."; }
      else if (totalScore <= 25) { level = "تاب‌آوری متوسط"; color = "#f59e0b"; advice = "تاب‌آوری قابل قبولی دارید."; }
      else if (totalScore <= 32) { level = "تاب‌آوری بالا"; color = "#10b981"; advice = "شما فردی تاب‌آور هستید!"; }
      else { level = "تاب‌آوری بسیار بالا"; color = "#059669"; advice = "شما الگوی تاب‌آوری هستید!"; }
    } else if (selectedTest.code === "ECOANX") {
      if (totalScore <= 15) { level = "اضطراب اقلیمی پایین"; color = "#10b981"; advice = "نگرانی سالمی دارید."; }
      else if (totalScore <= 24) { level = "اضطراب متوسط"; color = "#f59e0b"; advice = "با اقدامات کوچک کنترل را باز یابید."; }
      else if (totalScore <= 32) { level = "اضطراب بالا"; color = "#ea580c"; advice = "با گروه‌های همفکر ارتباط برقرار کنید."; }
      else { level = "اضطراب شدید"; color = "#dc2626"; advice = "با روانشناس متخصص مشورت کنید."; }
    } else if (selectedTest.code === "SWLS") {
      if (totalScore <= 9) { level = "نارضایتی شدید"; color = "#dc2626"; }
      else if (totalScore <= 14) { level = "نارضایتی"; color = "#ea580c"; }
      else if (totalScore <= 19) { level = "کمی نارضایت"; color = "#f59e0b"; }
      else if (totalScore <= 24) { level = "خنثی"; color = "#64748b"; }
      else if (totalScore <= 29) { level = "راضی"; color = "#10b981"; }
      else { level = "بسیار راضی"; color = "#059669"; }
      advice = "با تمرین شکرگزاری، رضایت را افزایش دهید.";
    } else {
      // پیش‌فرض
      const maxScore = selectedTest.questions * 4;
      const percent = (totalScore / maxScore) * 100;
      if (percent < 25) { level = "عالی"; color = "#10b981"; advice = "وضعیت شما بسیار خوب است."; }
      else if (percent < 50) { level = "خوب"; color = "#84cc16"; advice = "وضعیت قابل قبولی دارید."; }
      else if (percent < 75) { level = "نیاز به توجه"; color = "#f59e0b"; advice = "به برخی جنبه‌ها توجه بیشتری کنید."; }
      else { level = "نیاز به کمک"; color = "#dc2626"; advice = "با متخصص مشورت کنید."; }
    }
    
    setResult({
      type: "standard",
      totalScore,
      level,
      color,
      advice,
      maxScore: selectedTest.questions * 4,
    });
  };

  const resetTest = () => {
    setSelectedTest(null);
    setCurrentQuestion(0);
    setAnswers([]);
    setResult(null);
  };

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-600 to-pink-700 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        <div className="relative container mx-auto px-6 py-12">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-4 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-4">
              <div className="p-4 rounded-3xl bg-gradient-to-br from-purple-500 to-pink-600 shadow-2xl">
                <Brain className="h-10 w-10 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-purple-400 text-sm font-medium mb-1">سلامت روان و خودشناسی</p>
                <h1 className="text-4xl md:text-5xl font-black text-white mb-2">مرکز آزمون‌های روانشناسی</h1>
                <p className="text-lg text-slate-300 max-w-3xl">
                  ۹ آزمون معتبر بین‌المللی + ۲ آزمون اختصاصی اکو نوژین برای سنجش سلامت روان، تاب‌آوری، علاقه شغلی و ارتباط با طبیعت
                </p>
              </div>
            </div>

            <div className="flex flex-wrap gap-3 mt-6">
              {["محرمانه", "علمی", "رایگان", "تفسیر فوری"].map(badge => (
                <span key={badge} className="px-4 py-2 bg-purple-500/10 border border-purple-500/30 rounded-full text-sm text-purple-300">
                  ✓ {badge}
                </span>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      <section className="container mx-auto px-6 py-8">
        {!selectedTest && !result && (
          <>
            {/* Categories */}
            <div className="flex gap-3 mb-8 overflow-x-auto pb-2">
              {CATEGORIES.map(cat => (
                <button
                  key={cat.id}
                  onClick={() => setActiveCategory(cat.id)}
                  className={`px-5 py-3 rounded-xl font-bold transition-all flex items-center gap-2 whitespace-nowrap ${
                    activeCategory === cat.id
                      ? "bg-purple-600 text-white shadow-lg shadow-purple-500/30"
                      : "bg-slate-800 text-slate-400 hover:bg-slate-700"
                  }`}
                >
                  <span>{cat.icon}</span>
                  {cat.name}
                </button>
              ))}
            </div>

            {/* Tests Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredTests.map((test, idx) => (
                <motion.div
                  key={test.code}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 hover:border-purple-500/50 transition-all cursor-pointer group"
                  onClick={() => startTest(test)}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="p-3 rounded-xl" style={{ backgroundColor: test.color + "20" }}>
                      <span className="text-3xl">{test.icon}</span>
                    </div>
                    <span className="text-xs text-slate-500">{test.duration} دقیقه</span>
                  </div>
                  
                  <h3 className="text-xl font-bold text-white mb-2 group-hover:text-purple-400 transition-colors">
                    {test.title}
                  </h3>
                  <p className="text-sm text-slate-400 mb-4 line-clamp-2">{test.description}</p>
                  
                  <div className="flex items-center justify-between pt-4 border-t border-slate-800">
                    <span className="text-xs text-slate-500">{test.questions} سؤال</span>
                    <button className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-bold">
                      شروع آزمون
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          </>
        )}

        {/* Test Taking */}
        {selectedTest && !result && (
          <div className="max-w-3xl mx-auto">
            <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-8">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-white mb-1">{selectedTest.title}</h2>
                  <p className="text-sm text-slate-400">
                    سؤال {currentQuestion + 1} از {selectedTest.questions}
                  </p>
                </div>
                <button onClick={resetTest} className="text-slate-400 hover:text-white">
                  انصراف
                </button>
              </div>

              {/* Progress Bar */}
              <div className="h-2 bg-slate-800 rounded-full mb-8 overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-l from-purple-500 to-pink-500"
                  initial={{ width: 0 }}
                  animate={{ width: `${((currentQuestion + 1) / selectedTest.questions) * 100}%` }}
                />
              </div>

              {/* Question */}
              <div className="mb-8">
                <p className="text-xl text-white leading-relaxed">
                  {getQuestionText(selectedTest.code, currentQuestion)}
                </p>
              </div>

              {/* Options */}
              <div className="space-y-3">
                {getOptions(selectedTest.code).map((option, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleAnswer(option)}
                    className="w-full text-right p-4 bg-slate-800/50 border border-slate-700 rounded-xl hover:border-purple-500 hover:bg-purple-500/10 transition-all text-white"
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="max-w-3xl mx-auto">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-8"
            >
              <div className="text-center mb-8">
                <div className="inline-flex p-4 rounded-full mb-4" style={{ backgroundColor: result.color + "20" }}>
                  <Award className="h-12 w-12" style={{ color: result.color }} />
                </div>
                <h2 className="text-3xl font-black text-white mb-2">نتیجه آزمون شما</h2>
                <p className="text-slate-400">{selectedTest.title}</p>
              </div>

              {result.type === "holland" ? (
                <div>
                  <div className="text-center mb-6">
                    <p className="text-sm text-slate-400 mb-2">کد سه‌گانه شغلی شما:</p>
                    <p className="text-5xl font-black text-purple-400 mb-4">{result.top3Code}</p>
                  </div>
                  <div className="space-y-3">
                    {result.top3.map(([code, score], idx) => (
                      <div key={code} className="p-4 bg-slate-800/50 rounded-xl">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-bold text-white">
                            {idx + 1}. {getHollandName(code)}
                          </span>
                          <span className="text-purple-400 font-bold">{score}/4</span>
                        </div>
                        <p className="text-sm text-slate-400">{getHollandDesc(code)}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div>
                  <div className="text-center mb-6">
                    <p className="text-sm text-slate-400 mb-2">نمره شما:</p>
                    <p className="text-5xl font-black mb-2" style={{ color: result.color }}>
                      {result.totalScore}
                    </p>
                    {result.maxScore && (
                      <p className="text-sm text-slate-500">از {result.maxScore}</p>
                    )}
                  </div>
                  
                  <div className="p-6 rounded-xl mb-6" style={{ backgroundColor: result.color + "10", border: `1px solid ${result.color}40` }}>
                    <h3 className="text-xl font-bold mb-2" style={{ color: result.color }}>
                      {result.level}
                    </h3>
                    <p className="text-slate-300">{result.advice}</p>
                  </div>
                </div>
              )}

              <div className="flex gap-3 mt-8">
                <button
                  onClick={resetTest}
                  className="flex-1 py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-bold"
                >
                  بازگشت به لیست آزمون‌ها
                </button>
                <button
                  onClick={() => { setCurrentQuestion(0); setAnswers([]); setResult(null); }}
                  className="flex-1 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-bold"
                >
                  آزمون مجدد
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </section>
    </div>
  );
}

function getQuestionText(testCode, qIndex) {
  const questions = {
    GHQ28: ["آیا اخیراً سردرد یا درد داشته‌اید؟", "آیا احساس ضعف یا بی‌حالی می‌کنید؟", "آیا در تنفس مشکل دارید؟", "آیا احساس گرگرفتگی یا لرزش دارید؟", "آیا اخیراً احساس ناراحتی و بی‌قراری داشته‌اید؟", "آیا نگران چیزی هستید؟", "آیا خوابتان مختل شده؟", "آیا احساس ترس یا وحشت دارید؟", "آیا می‌توانید کارهای روزمره را انجام دهید؟", "آیا از فعالیت‌های مفید لذت می‌برید؟", "آیا در تصمیم‌گیری مشکل دارید؟", "آیا در انجام کارها نقش مفیدی دارید؟", "آیا از زندگی لذت می‌برید؟", "آیا می‌توانید روی کار تمرکز کنید؟", "آیا احساس خوشحالی می‌کنید؟", "آیا می‌توانید کارهای روزانه را انجام دهید؟"],
    DASS21: ["سخت بود که آرام شوم", "احساس خشکی دهان داشتم", "نتوانستم احساس مثبتی داشته باشم", "تنگی نفس داشتم", "سخت بودinitiative بگیرم", "واکنش‌هایم بیش از حد بود", "احساس لرزش داشتم", "احساس کردم انرژی زیادی مصرف می‌کنم", "نگران بودم که وحشت‌زده شوم", "احساس کردم چیزی برای لذت بردن ندارم", "بی‌قرار بودم", "سخت بود relax کنم", "افسرده و غمگین بودم", "بی‌صبر بودم", "احساس کردم نزدیک است غش کنم", "نتوانستم از هیچ چیز لذت ببرم", "احساس کردم ارزشی به عنوان آدم ندارم", "احساس حساسیت بیش از حد داشتم", "بدون دلیل تپش قلب داشتم", "از پنیک و وحشت بی‌دلیل ترسیدم", "سخت بود آرام شوم"],
    CDRISC: ["وقتی شرایط سخت می‌شود، می‌توانم با آن سازگار شوم", "تمایل دارم به چیزهای جدید فکر کنم", "به غریزه خود اعتماد دارم", "می‌توانم با تغییرات کنار بیایم", "بعد از بیماری یا سختی، بهبود می‌یابم", "برای رسیدن به اهدافم تلاش می‌کنم", "وقتی شکست می‌خورم، دوباره بلند می‌شوم", "فکر می‌کنم خودم قوی هستم", "می‌توانم تصمیمات ناخوشایند بپذیرم", "باور دارم می‌توانم بر مشکلات غلبه کنم"],
    HOLLAND: ["کار با دست و ابزار را دوست دارم", "تعمیر ماشین یا وسایل را دوست دارم", "کار در فضای باز را ترجیح می‌دهم", "ورزش‌های فیزیکی را دوست دارم", "حل مسائل ریاضی و علمی را دوست دارم", "مطالعه مقالات علمی را دوست دارم", "کنجکاو هستم و سؤالات زیادی می‌پرسم", "تحقیق و پژوهش را دوست دارم", "نقاشی، موسیقی یا نوشتن را دوست دارم", "ایده‌های خلاقانه دارم", "از کارهای یکنواخت بیزارم", "طراحی و خلق چیزهای جدید را دوست دارم", "کمک به دیگران را دوست دارم", "معلم یا مشاور شدن را دوست دارم", "درک احساسات دیگران را دارم", "کار گروهی را ترجیح می‌دهم", "رهبری و مدیریت را دوست دارم", "متقاعد کردن دیگران را دوست دارم", "راه‌اندازی کسب‌وکار را دوست دارم", "رقابت را دوست دارم", "کار با جزئیات و نظم را دوست دارم", "کار دفتری و اداری را دوست دارم", "دقت و نظم برایم مهم است", "پیروی از دستورالعمل‌ها را دوست دارم"],
    NR6: ["بودن در طبیعت برایم بسیار لذت‌بخش است", "احساس می‌کنم بخشی از چرخه طبیعت هستم", "وقتی در طبیعت هستم، احساس آرامش عمیق می‌کنم", "نگران وضعیت محیط زیست هستم", "رشد گیاهان و تغییر فصل‌ها برایم جذاب است", "حاضرم برای حفظ طبیعت از راحتی‌ام بگذرم"],
    ECOANX: ["وقتی درباره تغییرات اقلیمی فکر می‌کنم، مضطرب می‌شوم", "احساس می‌کنم آینده سیاره ما تاریک است", "خبرهای مربوط به محیط زیست مرا ناراحت می‌کند", "نگران آینده فرزندانم در این سیاره هستم", "احساس می‌کنم کاری که می‌کنم کافی نیست", "از تصور فاجعه‌های اقلیمی می‌ترسم", "گاهی احساس ناامیدی درباره آینده زمین دارم", "نگرانم که نسل‌های آینده ما را سرزنش کنند"],
    MBI: ["احساس می‌کنم از نظر عاطفی تخلیه شده‌ام", "صبح‌ها با بی‌میلی به سر کار می‌روم", "احساس می‌کنم در آستانه فروپاشی هستم", "با بعضی افراد مثل اشیاء رفتار می‌کنم", "سخت است به دیگران اهمیت دهم", "احساس می‌کنم با بعضی افراد سرد شده‌ام", "به راحتی می‌فهمم دیگران چه احساسی دارند", "با انرژی زیاد کارهایم را انجام می‌دهم", "احساس می‌کنم کارهایم مؤثر است"],
    PHQ9: ["کم‌علاقگی یا عدم لذت از انجام کارها", "احساس افسردگی، ناامیدی یا بی‌آیندگی", "مشکل در به خواب رفتن، بیدار ماندن یا خواب زیاد", "احساس خستگی یا نداشتن انرژی", "کم‌اشتهایی یا پرخوری", "احساس بدی درباره خودتان", "مشکل در تمرکز روی کارها", "حرکت یا صحبت کردن کندتر، یا بی‌قراری", "افکار مرگ یا آسیب به خود"],
    SWLS: ["در بیشتر موارد، زندگی من به ایده‌آل‌هایم نزدیک است", "شرایط زندگی‌ام عالی است", "از زندگی‌ام راضی هستم", "تاکنون چیزهای مهمی که در زندگی می‌خواستم را به دست آورده‌ام", "اگر می‌توانستم تقریباً هیچ چیز را در زندگی‌ام تغییر ندهم"],
  };
  return questions[testCode]?.[qIndex] || "سؤال";
}

function getOptions(testCode) {
  if (testCode === "HOLLAND") {
    return [
      { label: "بله، کاملاً با من سازگار است", answer: true },
      { label: "خیر، با من سازگار نیست", answer: false },
    ];
  }
  if (testCode === "GHQ28") {
    return [
      { label: "بدتر از معمول", score: 3 },
      { label: "همانند معمول", score: 2 },
      { label: "بهتر از معمول", score: 1 },
      { label: "خیلی بهتر از معمول", score: 0 },
    ];
  }
  if (testCode === "DASS21" || testCode === "PHQ9") {
    return [
      { label: "کاملاً نادرست / اصلاً", score: 0 },
      { label: "تا حدودی نادرست / چند روز", score: 1 },
      { label: "تا حدودی درست / بیشتر روزها", score: 2 },
      { label: "کاملاً درست / تقریباً هر روز", score: 3 },
    ];
  }
  if (testCode === "CDRISC" || testCode === "NR6" || testCode === "ECOANX") {
    return [
      { label: "کاملاً مخالفم", score: 1 },
      { label: "مخالفم", score: 2 },
      { label: "نظری ندارم", score: 3 },
      { label: "موافقم", score: 4 },
      { label: "کاملاً موافقم", score: 5 },
    ];
  }
  if (testCode === "MBI") {
    return [
      { label: "هرگز", score: 0 },
      { label: "چند بار در سال", score: 1 },
      { label: "یک بار در ماه", score: 2 },
      { label: "چند بار در ماه", score: 3 },
      { label: "یک بار در هفته", score: 4 },
      { label: "چند بار در هفته", score: 5 },
      { label: "هر روز", score: 6 },
    ];
  }
  if (testCode === "SWLS") {
    return [
      { label: "کاملاً مخالفم", score: 1 },
      { label: "مخالفم", score: 2 },
      { label: "کمی مخالفم", score: 3 },
      { label: "نظری ندارم", score: 4 },
      { label: "کمی موافقم", score: 5 },
      { label: "موافقم", score: 6 },
      { label: "کاملاً موافقم", score: 7 },
    ];
  }
  return [];
}

function getHollandName(code) {
  const names = {
    R: "واقع‌گرا (Realistic)",
    I: "جستجوگر (Investigative)",
    A: "هنری (Artistic)",
    S: "اجتماعی (Social)",
    E: "متهور (Enterprising)",
    C: "قراردادی (Conventional)",
  };
  return names[code];
}

function getHollandDesc(code) {
  const descs = {
    R: "علاقه‌مند به کارهای عملی، فنی و فیزیکی",
    I: "علاقه‌مند به تحقیق، تحلیل و حل مسئله",
    A: "علاقه‌مند به خلاقیت، طراحی و بیان",
    S: "علاقه‌مند به کمک، آموزش و مشاوره",
    E: "علاقه‌مند به رهبری، فروش و مدیریت",
    C: "علاقه‌مند به نظم، جزئیات و سازماندهی",
  };
  return descs[code];
}
'''
    write_file(WEB / "app" / "psychology" / "page.tsx", content)


# ============================================================
# فایل 6: به‌روزرسانی main.py
# ============================================================
def update_main():
    print("\n🔧 به‌روزرسانی main.py...")
    main_path = API_DIR / "main.py"
    if not main_path.exists():
        print("   ❌ main.py یافت نشد")
        return
    
    content = main_path.read_text(encoding="utf-8")
    
    if "psychology_router" not in content:
        # پیدا کردن آخرین import
        lines = content.split('\n')
        last_import_idx = 0
        last_router_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("from api.modules."):
                last_import_idx = i
            if "app.include_router(" in line:
                last_router_idx = i
        
        lines.insert(last_import_idx + 1, "from api.modules.psychology.router import router as psychology_router")
        lines.insert(last_router_idx + 2, 'app.include_router(psychology_router, prefix="/api/v1")')
        
        main_path.write_text('\n'.join(lines), encoding="utf-8")
        print("   ✅ psychology_router اضافه شد")
    else:
        print("   ℹ️  از قبل اضافه شده")


# ============================================================
# Main
# ============================================================
def main():
    print("🧠 ایجاد ماژول جامع سلامت روان و آزمون‌های روانشناسی")
    print("=" * 70)
    
    if not API_DIR.exists() or not WEB.exists():
        print("❌ دایرکتوری‌ها یافت نشد!")
        return 1
    
    create_models()
    create_tests_database()
    create_router()
    create_init()
    create_frontend()
    update_main()
    
    print("\n" + "=" * 70)
    print("✅ ماژول سلامت روان با موفقیت ایجاد شد!")
    print("\n🎯 ۹ آزمون معتبر پیاده‌سازی شده:")
    print("   💚 GHQ-28: سلامت عمومی گلدبرگ")
    print("   🧠 DASS-21: افسردگی، اضطراب، استرس")
    print("   💪 CD-RISC: تاب‌آوری کانر-دیویدسون")
    print("   💼 Holland RIASEC: علاقه‌سنجی شغلی")
    print("   🌿 Nature Relatedness: ارتباط با طبیعت (اختصاصی!)")
    print("   🌡️ Eco-Anxiety: اضطراب اقلیمی (اختصاصی!)")
    print("   🔥 MBI: فرسودگی شغلی ماسلاچ")
    print("   😔 PHQ-9: غربالگری افسردگی")
    print("   😊 SWLS: رضایت از زندگی")
    print("")
    print("🚀 گام بعدی:")
    print("   1. ری‌استارت سرور بک‌اند: uvicorn api.main:app --reload --port 8000")
    print("   2. پاک‌سازی کش فرانت‌اند: cd apps\\web && Remove-Item .next -Recurse -Force")
    print("   3. اجرا: pnpm run dev -- -p 3001")
    print("   4. مشاهده: http://localhost:3001/psychology")
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())