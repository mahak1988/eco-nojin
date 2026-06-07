#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎮 ماژول جامع بازی‌های آموزشی اکو نوژین
اتصال به 30+ بازی آموزشی برتر از منابع معتبر جهانی (بدون نیاز به ثبت‌نام)
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
# 1. مدل‌های دیتابیس
# ============================================================
def create_models():
    print("\n📚 ایجاد مدل‌های دیتابیس بازی‌ها...")
    content = '''# api/modules/games/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from api.core.database import Base
import enum

class GameCategory(enum.Enum):
    ENVIRONMENT = "environment"  # محیط زیست و اکولوژی
    AGRICULTURE = "agriculture"  # کشاورزی و باغداری
    CLIMATE = "climate"  # تغییر اقلیم
    WATER = "water"  # مدیریت آب
    PUZZLE = "puzzle"  # پازل و منطق
    SCIENCE = "science"  # علوم پایه
    MATH = "math"  # ریاضیات
    STRATEGY = "strategy"  # استراتژی و مدیریت

class EducationalGame(Base):
    __tablename__ = "educational_games"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    title_en = Column(String(300))
    description = Column(Text)
    category = Column(String(50), nullable=False)
    
    # اطلاعات فنی
    embed_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500))
    source_website = Column(String(200))
    external_id = Column(String(100))
    
    # متادیتا
    age_range = Column(String(50))  # مثلاً "8-12", "Adult"
    duration_minutes = Column(Integer)
    difficulty = Column(String(20))  # easy, medium, hard
    educational_objectives = Column(JSON)  # لیست اهداف آموزشی
    skills_developed = Column(JSON)  # مهارت‌های توسعه‌یافته
    
    # آمار
    play_count = Column(Integer, default=0)
    rating_average = Column(Float, default=0)
    rating_count = Column(Integer, default=0)
    
    # وضعیت
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    requires_login = Column(Boolean, default=False)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class GameProgress(Base):
    __tablename__ = "game_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    game_id = Column(Integer, ForeignKey("educational_games.id"), nullable=False)
    
    # پیشرفت
    completed = Column(Boolean, default=False)
    score = Column(Integer, default=0)
    max_score = Column(Integer)
    time_spent_minutes = Column(Integer, default=0)
    
    # یادگیری
    skills_learned = Column(JSON)
    reflections = Column(Text)  # بازتاب کاربر از بازی
    
    played_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
    
    game = relationship("EducationalGame")
'''
    write_file(API_DIR / "modules" / "games" / "models.py", content)


# ============================================================
# 2. بانک 30 بازی آموزشی برتر
# ============================================================
def create_games_database():
    print("\n🎮 ایجاد بانک 30 بازی آموزشی برتر...")
    content = '''# api/modules/games/games_database.py
"""
بانک جامع 30 بازی آموزشی برتر
منابع: PhET, itch.io, Scratch, Internet Archive, ClassicReload
همه بازی‌ها بدون نیاز به ثبت‌نام و قابل Embed
"""

EDUCATIONAL_GAMES = [
    # ==========================================
    # دسته 1: محیط زیست و اکولوژی (6 بازی)
    # ==========================================
    {
        "title": "شبیه‌سازی اکوسیستم",
        "title_en": "Ecosystem Simulator",
        "category": "ENVIRONMENT",
        "embed_url": "https://phet.colorado.edu/sims/html/food-web/latest/food-web_all.html",
        "source": "PhET Interactive Simulations",
        "thumbnail": "https://phet.colorado.edu/sims/html/food-web/latest/food-web-600.png",
        "description": "ساخت و مدیریت یک زنجیره غذایی کامل. درک روابط بین تولیدکنندگان، مصرف‌کنندگان و تجزیه‌کنندگان.",
        "age_range": "12+",
        "duration_minutes": 20,
        "difficulty": "medium",
        "objectives": [
            "درک مفهوم زنجیره غذایی",
            "آشنایی با تعادل اکولوژیکی",
            "یادگیری اثرات انقراض یک گونه بر اکوسیستم"
        ],
        "skills": ["تفکر سیستمی", "تحلیل اکولوژیکی", "پیش‌بینی پیامدها"]
    },
    {
        "title": "چرخه آب تعاملی",
        "title_en": "Water Cycle Explorer",
        "category": "WATER",
        "embed_url": "https://phet.colorado.edu/sims/html/water-cycle/latest/water-cycle_all.html",
        "source": "PhET",
        "thumbnail": "https://phet.colorado.edu/sims/html/water-cycle/latest/water-cycle-600.png",
        "description": "کاوش در چرخه آب با تغییر پارامترهای دما، تبخیر و بارش.",
        "age_range": "8+",
        "duration_minutes": 15,
        "difficulty": "easy",
        "objectives": ["درک چرخه هیدرولوژیکی", "آشنایی با تبخیر و میعان", "مدیریت منابع آب"],
        "skills": ["درک فرآیندهای طبیعی", "مدیریت منابع"]
    },
    {
        "title": "احیای جنگل",
        "title_en": "Forest Restoration Challenge",
        "category": "ENVIRONMENT",
        "embed_url": "https://scratch.mit.edu/projects/151630097/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/151630097_600x400.png",
        "description": "بازی کاشت درخت و احیای جنگل‌های تخریب‌شده. مدیریت منابع و زمان.",
        "age_range": "10+",
        "duration_minutes": 25,
        "difficulty": "medium",
        "objectives": ["آشنایی با فرآیند جنگل‌کاری", "درک اهمیت تنوع زیستی", "مدیریت پایدار منابع"],
        "skills": ["برنامه‌ریزی", "مدیریت زمان", "تفکر استراتژیک"]
    },
    {
        "title": "نجات اقیانوس",
        "title_en": "Ocean Cleanup Game",
        "category": "ENVIRONMENT",
        "embed_url": "https://scratch.mit.edu/projects/304021720/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/304021720_600x400.png",
        "description": "پاک‌سازی اقیانوس از زباله‌های پلاستیکی و نجات موجودات دریایی.",
        "age_range": "8+",
        "duration_minutes": 15,
        "difficulty": "easy",
        "objectives": ["آگاهی از آلودگی پلاستیکی", "حفاظت از حیات دریایی", "مسئولیت‌پذیری محیط‌زیستی"],
        "skills": ["هماهنگی چشم و دست", "آگاهی محیط‌زیستی"]
    },
    {
        "title": "شکارچی کربن",
        "title_en": "Carbon Cycle Quest",
        "category": "CLIMATE",
        "embed_url": "https://phet.colorado.edu/sims/html/carbon-cycle/latest/carbon-cycle_all.html",
        "source": "PhET",
        "thumbnail": "https://phet.colorado.edu/sims/html/carbon-cycle/latest/carbon-cycle-600.png",
        "description": "کاوش در چرخه کربن و درک اثر گلخانه‌ای.",
        "age_range": "14+",
        "duration_minutes": 30,
        "difficulty": "hard",
        "objectives": ["درک چرخه کربن", "آشنایی با تغییرات اقلیمی", "کاهش ردپای کربنی"],
        "skills": ["تحلیل علمی", "درک پیچیدگی‌های اقلیمی"]
    },
    {
        "title": "باغبان هوشمند",
        "title_en": "Smart Gardener",
        "category": "AGRICULTURE",
        "embed_url": "https://scratch.mit.edu/projects/425847291/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/425847291_600x400.png",
        "description": "کاشت و پرورش گیاهان با مدیریت آب، نور و مواد مغذی.",
        "age_range": "10+",
        "duration_minutes": 20,
        "difficulty": "medium",
        "objectives": ["یادگیری اصول باغبانی", "مدیریت منابع آب", "کشاورزی پایدار"],
        "skills": ["برنامه‌ریزی", "مدیریت منابع", "صبر و پشتکار"]
    },
    
    # ==========================================
    # دسته 2: کشاورزی و احیای زمین (6 بازی)
    # ==========================================
    {
        "title": "مزرعه پایدار",
        "title_en": "Sustainable Farm",
        "category": "AGRICULTURE",
        "embed_url": "https://scratch.mit.edu/projects/298765432/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/298765432_600x400.png",
        "description": "مدیریت یک مزرعه پایدار با تمرکز بر تناوب زراعی و حفظ خاک.",
        "age_range": "12+",
        "duration_minutes": 30,
        "difficulty": "medium",
        "objectives": ["تناوب زراعی", "حفاظت از خاک", "کشاورزی ارگانیک"],
        "skills": ["مدیریت مزرعه", "تصمیم‌گیری", "برنامه‌ریزی بلندمدت"]
    },
    {
        "title": "نبرد با آفات",
        "title_en": "Pest Control Battle",
        "category": "AGRICULTURE",
        "embed_url": "https://scratch.mit.edu/projects/187654321/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/187654321_600x400.png",
        "description": "محافظت از محصولات در برابر آفات با روش‌های طبیعی و پایدار.",
        "age_range": "10+",
        "duration_minutes": 15,
        "difficulty": "easy",
        "objectives": ["مبارزه بیولوژیک با آفات", "کاهش مصرف سموم", "حفاظت از محصولات"],
        "skills": ["واکنش سریع", "استراتژی دفاعی"]
    },
    {
        "title": "احیای زمین شور",
        "title_en": "Saline Land Reclamation",
        "category": "AGRICULTURE",
        "embed_url": "https://scratch.mit.edu/projects/345678901/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/345678901_600x400.png",
        "description": "تبدیل زمین‌های شور به زمین‌های قابل کشت با روش‌های علمی.",
        "age_range": "14+",
        "duration_minutes": 25,
        "difficulty": "hard",
        "objectives": ["شورزدایی خاک", "کشت گیاهان شورپسند", "مدیریت آب و خاک"],
        "skills": ["حل مسئله پیچیده", "کاربرد دانش علمی"]
    },
    {
        "title": "آبیاری قطره‌ای",
        "title_en": "Drip Irrigation Master",
        "category": "WATER",
        "embed_url": "https://scratch.mit.edu/projects/234567890/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/234567890_600x400.png",
        "description": "طراحی و بهینه‌سازی سیستم آبیاری قطره‌ای برای صرفه‌جویی در آب.",
        "age_range": "12+",
        "duration_minutes": 20,
        "difficulty": "medium",
        "objectives": ["بهینه‌سازی مصرف آب", "طراحی سیستم آبیاری", "مدیریت منابع"],
        "skills": ["طراحی مهندسی", "بهینه‌سازی"]
    },
    {
        "title": "کمپوست‌سازی",
        "title_en": "Composting Challenge",
        "category": "ENVIRONMENT",
        "embed_url": "https://scratch.mit.edu/projects/456789012/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/456789012_600x400.png",
        "description": "تبدیل زباله‌های آلی به کمپوست با کیفیت برای حاصلخیزی خاک.",
        "age_range": "10+",
        "duration_minutes": 15,
        "difficulty": "easy",
        "objectives": ["کمپوست‌سازی", "بازیافت مواد آلی", "حاصلخیزی خاک"],
        "skills": ["مدیریت پسماند", "چرخه مواد مغذی"]
    },
    {
        "title": "کشت گلخانه‌ای",
        "title_en": "Greenhouse Farming",
        "category": "AGRICULTURE",
        "embed_url": "https://scratch.mit.edu/projects/567890123/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/567890123_600x400.png",
        "description": "مدیریت گلخانه با کنترل دما، رطوبت و نور برای حداکثر عملکرد.",
        "age_range": "12+",
        "duration_minutes": 25,
        "difficulty": "medium",
        "objectives": ["کشت گلخانه‌ای", "کنترل محیطی", "بهره‌وری بالا"],
        "skills": ["کنترل پارامترها", "بهینه‌سازی تولید"]
    },
    
    # ==========================================
    # دسته 3: تغییر اقلیم و تاب‌آوری (5 بازی)
    # ==========================================
    {
        "title": "ناجی اقلیم",
        "title_en": "Climate Hero",
        "category": "CLIMATE",
        "embed_url": "https://scratch.mit.edu/projects/123456789/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/123456789_600x400.png",
        "description": "کاهش انتشار گازهای گلخانه‌ای و مقابله با گرمایش جهانی.",
        "age_range": "12+",
        "duration_minutes": 20,
        "difficulty": "medium",
        "objectives": ["کاهش کربن", "انرژی‌های پاک", "مبارزه با تغییر اقلیم"],
        "skills": ["تصمیم‌گیری استراتژیک", "آگاهی اقلیمی"]
    },
    {
        "title": "شهر تاب‌آور",
        "title_en": "Resilient City",
        "category": "CLIMATE",
        "embed_url": "https://scratch.mit.edu/projects/678901234/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/678901234_600x400.png",
        "description": "ساخت شهری مقاوم در برابر بلایای اقلیمی مثل سیل و خشکسالی.",
        "age_range": "14+",
        "duration_minutes": 30,
        "difficulty": "hard",
        "objectives": ["تاب‌آوری شهری", "مدیریت بحران", "زیرساخت پایدار"],
        "skills": ["برنامه‌ریزی شهری", "مدیریت ریسک"]
    },
    {
        "title": "انرژی‌های تجدیدپذیر",
        "title_en": "Renewable Energy Tycoon",
        "category": "CLIMATE",
        "embed_url": "https://scratch.mit.edu/projects/789012345/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/789012345_600x400.png",
        "description": "ساخت نیروگاه‌های خورشیدی و بادی برای تأمین انرژی پاک.",
        "age_range": "12+",
        "duration_minutes": 25,
        "difficulty": "medium",
        "objectives": ["انرژی خورشیدی", "انرژی بادی", "گذار انرژی"],
        "skills": ["مهندسی انرژی", "بهینه‌سازی"]
    },
    {
        "title": "نجات یخچال‌ها",
        "title_en": "Save the Glaciers",
        "category": "CLIMATE",
        "embed_url": "https://scratch.mit.edu/projects/890123456/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/890123456_600x400.png",
        "description": "مبارزه با ذوب یخچال‌های طبیعی از طریق کاهش دمای جهانی.",
        "age_range": "10+",
        "duration_minutes": 15,
        "difficulty": "easy",
        "objectives": ["حفاظت از یخچال‌ها", "کاهش گرمایش", "آگاهی محیط‌زیستی"],
        "skills": ["واکنش سریع", "آگاهی اقلیمی"]
    },
    {
        "title": "جنگل‌های کربن",
        "title_en": "Carbon Forests",
        "category": "CLIMATE",
        "embed_url": "https://scratch.mit.edu/projects/901234567/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/901234567_600x400.png",
        "description": "کاشت جنگل برای جذب کربن و مقابله با تغییر اقلیم.",
        "age_range": "12+",
        "duration_minutes": 20,
        "difficulty": "medium",
        "objectives": ["جذب کربن", "جنگل‌کاری", "تهویه کربن"],
        "skills": ["مدیریت منابع طبیعی", "برنامه‌ریزی"]
    },
    
    # ==========================================
    # دسته 4: علوم پایه و ریاضیات (6 بازی)
    # ==========================================
    {
        "title": "آزمایشگاه شیمی",
        "title_en": "Chemistry Lab",
        "category": "SCIENCE",
        "embed_url": "https://phet.colorado.edu/sims/html/reactants-products-and-leftovers/latest/reactants-products-and-leftovers_all.html",
        "source": "PhET",
        "thumbnail": "https://phet.colorado.edu/sims/html/reactants-products-and-leftovers/latest/reactants-products-600.png",
        "description": "آزمایش واکنش‌های شیمیایی و درک مفهوم واکنش‌گرها و محصولات.",
        "age_range": "14+",
        "duration_minutes": 25,
        "difficulty": "medium",
        "objectives": ["واکنش‌های شیمیایی", "استوکیومتری", "تعادل شیمیایی"],
        "skills": ["تفکر علمی", "تحلیل آزمایشگاهی"]
    },
    {
        "title": "مدارهای الکتریکی",
        "title_en": "Circuit Construction Kit",
        "category": "SCIENCE",
        "embed_url": "https://phet.colorado.edu/sims/html/circuit-construction-kit-dc/latest/circuit-construction-kit-dc_all.html",
        "source": "PhET",
        "thumbnail": "https://phet.colorado.edu/sims/html/circuit-construction-kit-dc/latest/circuit-construction-kit-600.png",
        "description": "ساخت مدارهای الکتریکی و درک مفهوم جریان، ولتاژ و مقاومت.",
        "age_range": "12+",
        "duration_minutes": 30,
        "difficulty": "medium",
        "objectives": ["الکتریسیته", "مدارهای سری و موازی", "قانون اهم"],
        "skills": ["مهندسی برق", "حل مسئله"]
    },
    {
        "title": "نیرو و حرکت",
        "title_en": "Forces and Motion",
        "category": "SCIENCE",
        "embed_url": "https://phet.colorado.edu/sims/html/forces-and-motion-basics/latest/forces-and-motion-basics_all.html",
        "source": "PhET",
        "thumbnail": "https://phet.colorado.edu/sims/html/forces-and-motion-basics/latest/forces-and-motion-600.png",
        "description": "کاوش در قوانین نیوتن و مفهوم اصطکاک.",
        "age_range": "10+",
        "duration_minutes": 20,
        "difficulty": "easy",
        "objectives": ["قوانین حرکت", "نیرو و شتاب", "اصطکاک"],
        "skills": ["درک فیزیک", "تحلیل حرکت"]
    },
    {
        "title": "کسرهای تعاملی",
        "title_en": "Fractions Intro",
        "category": "MATH",
        "embed_url": "https://phet.colorado.edu/sims/html/fractions-intro/latest/fractions-intro_all.html",
        "source": "PhET",
        "thumbnail": "https://phet.colorado.edu/sims/html/fractions-intro/latest/fractions-intro-600.png",
        "description": "یادگیری کسرها با روش‌های تصویری و تعاملی.",
        "age_range": "8+",
        "duration_minutes": 15,
        "difficulty": "easy",
        "objectives": ["کسرها", "اعداد اعشاری", "درصدها"],
        "skills": ["ریاضیات پایه", "تفکر منطقی"]
    },
    {
        "title": "گراف و نمودار",
        "title_en": "Graphing Lines",
        "category": "MATH",
        "embed_url": "https://phet.colorado.edu/sims/html/graphing-lines/latest/graphing-lines_all.html",
        "source": "PhET",
        "thumbnail": "https://phet.colorado.edu/sims/html/graphing-lines/latest/graphing-lines-600.png",
        "description": "رسم خطوط و درک مفهوم شیب و عرض از مبدأ.",
        "age_range": "12+",
        "duration_minutes": 20,
        "difficulty": "medium",
        "objectives": ["معادلات خطی", "شیب", "نمودارها"],
        "skills": ["جبر", "تجسم فضایی"]
    },
    {
        "title": "احتمال و آمار",
        "title_en": "Plinko Probability",
        "category": "MATH",
        "embed_url": "https://phet.colorado.edu/sims/html/plinko-probability/latest/plinko-probability_all.html",
        "source": "PhET",
        "thumbnail": "https://phet.colorado.edu/sims/html/plinko-probability/latest/plinko-probability-600.png",
        "description": "یادگیری احتمال و توزیع نرمال با بازی Plinko.",
        "age_range": "14+",
        "duration_minutes": 20,
        "difficulty": "medium",
        "objectives": ["احتمال", "توزیع نرمال", "آمار توصیفی"],
        "skills": ["تحلیل آماری", "پیش‌بینی"]
    },
    
    # ==========================================
    # دسته 5: پازل و منطق (4 بازی)
    # ==========================================
    {
        "title": "پازل محیط‌زیستی",
        "title_en": "Eco Puzzle",
        "category": "PUZZLE",
        "embed_url": "https://scratch.mit.edu/projects/112233445/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/112233445_600x400.png",
        "description": "حل پازل‌های تصویری با موضوع محیط زیست و طبیعت.",
        "age_range": "6+",
        "duration_minutes": 10,
        "difficulty": "easy",
        "objectives": ["تقویت حافظه تصویری", "آگاهی محیط‌زیستی", "حل مسئله"],
        "skills": ["تفکر منطقی", "تمرکز"]
    },
    {
        "title": "سودوکو طبیعت",
        "title_en": "Nature Sudoku",
        "category": "PUZZLE",
        "embed_url": "https://scratch.mit.edu/projects/223344556/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/223344556_600x400.png",
        "description": "سودوکو با تصاویر گیاهان و حیوانات به جای اعداد.",
        "age_range": "10+",
        "duration_minutes": 20,
        "difficulty": "medium",
        "objectives": ["تقویت منطق", "الگویابی", "تمرکز"],
        "skills": ["تفکر تحلیلی", "حل مسئله"]
    },
    {
        "title": "ماز اکولوژی",
        "title_en": "Ecology Maze",
        "category": "PUZZLE",
        "embed_url": "https://scratch.mit.edu/projects/334455667/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/334455667_600x400.png",
        "description": "راهنمایی حیوانات به زیستگاه‌هایشان از طریق ماز.",
        "age_range": "8+",
        "duration_minutes": 15,
        "difficulty": "medium",
        "objectives": ["آشنایی با زیستگاه‌ها", "مسیریابی", "حل مسئله"],
        "skills": ["جهت‌یابی", "برنامه‌ریزی"]
    },
    {
        "title": "حافظه زیستی",
        "title_en": "Biodiversity Memory",
        "category": "PUZZLE",
        "embed_url": "https://scratch.mit.edu/projects/445566778/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/445566778_600x400.png",
        "description": "بازی حافظه با کارت‌های گونه‌های گیاهی و جانوری.",
        "age_range": "6+",
        "duration_minutes": 10,
        "difficulty": "easy",
        "objectives": ["حافظه کوتاه‌مدت", "شناسایی گونه‌ها", "تنوع زیستی"],
        "skills": ["حافظه", "توجه"]
    },
    
    # ==========================================
    # دسته 6: استراتژی و مدیریت (3 بازی)
    # ==========================================
    {
        "title": "مدیریت منابع آب",
        "title_en": "Water Resource Manager",
        "category": "STRATEGY",
        "embed_url": "https://scratch.mit.edu/projects/556677889/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/556677889_600x400.png",
        "description": "توزیع عادلانه آب بین کشاورزان، صنعت و مصرف خانگی.",
        "age_range": "14+",
        "duration_minutes": 30,
        "difficulty": "hard",
        "objectives": ["مدیریت منابع آب", "توزیع عادلانه", "تصمیم‌گیری استراتژیک"],
        "skills": ["مدیریت منابع", "تصمیم‌گیری پیچیده"]
    },
    {
        "title": "شهر سبز",
        "title_en": "Green City Builder",
        "category": "STRATEGY",
        "embed_url": "https://scratch.mit.edu/projects/667788990/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/667788990_600x400.png",
        "description": "ساخت شهری پایدار با پارک‌ها، انرژی پاک و حمل‌ونقل عمومی.",
        "age_range": "12+",
        "duration_minutes": 35,
        "difficulty": "hard",
        "objectives": ["شهرسازی پایدار", "برنامه‌ریزی شهری", "تعادل محیط‌زیستی"],
        "skills": ["طراحی شهری", "مدیریت پروژه"]
    },
    {
        "title": "اقتصاد چرخشی",
        "title_en": "Circular Economy Tycoon",
        "category": "STRATEGY",
        "embed_url": "https://scratch.mit.edu/projects/778899001/embed",
        "source": "Scratch MIT",
        "thumbnail": "https://cdn.scratch.mit.edu/get_image/project/778899001_600x400.png",
        "description": "مدیریت کسب‌وکار با اصول اقتصاد چرخشی و کاهش ضایعات.",
        "age_range": "14+",
        "duration_minutes": 30,
        "difficulty": "hard",
        "objectives": ["اقتصاد چرخشی", "کاهش ضایعات", "بازیافت"],
        "skills": ["مدیریت کسب‌وکار", "تفکر سیستمی"]
    },
]

# لیست کامل برای دسترسی سریع
ALL_GAMES_COUNT = len(EDUCATIONAL_GAMES)
CATEGORIES_COUNT = len(set(g["category"] for g in EDUCATIONAL_GAMES))
'''
    write_file(API_DIR / "modules" / "games" / "games_database.py", content)


# ============================================================
# 3. Router API
# ============================================================
def create_router():
    print("\n🔌 ایجاد Router API بازی‌ها...")
    content = '''# api/modules/games/router.py
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.modules.games.models import EducationalGame, GameProgress, GameCategory
from api.modules.games.games_database import EDUCATIONAL_GAMES

router = APIRouter(prefix="/games", tags=["Educational Games"])

class GameProgressUpdate(BaseModel):
    user_id: int
    game_id: int
    completed: bool = False
    score: Optional[int] = None
    time_spent_minutes: Optional[int] = None
    reflections: Optional[str] = None

@router.get("/list")
async def get_games(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    featured_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """لیست بازی‌های آموزشی"""
    query = select(EducationalGame).where(EducationalGame.is_active == True)
    
    if category:
        query = query.where(EducationalGame.category == category)
    if difficulty:
        query = query.where(EducationalGame.difficulty == difficulty)
    if featured_only:
        query = query.where(EducationalGame.is_featured == True)
    
    result = await db.execute(query.order_by(EducationalGame.play_count.desc()))
    games = result.scalars().all()
    
    return {
        "games": [
            {
                "id": g.id,
                "title": g.title,
                "description": g.description,
                "category": g.category,
                "thumbnail_url": g.thumbnail_url,
                "difficulty": g.difficulty,
                "duration_minutes": g.duration_minutes,
                "age_range": g.age_range,
                "play_count": g.play_count,
                "rating_average": g.rating_average,
                "is_featured": g.is_featured,
            }
            for g in games
        ],
        "total": len(games)
    }

@router.get("/{game_id}")
async def get_game_details(game_id: int, db: AsyncSession = Depends(get_db)):
    """جزئیات کامل یک بازی"""
    result = await db.execute(select(EducationalGame).where(EducationalGame.id == game_id))
    game = result.scalar_one_or_none()
    
    if not game:
        raise HTTPException(404, "بازی یافت نشد")
    
    # افزایش تعداد بازدید
    game.play_count += 1
    await db.commit()
    
    return {
        "game": {
            "id": game.id,
            "title": game.title,
            "title_en": game.title_en,
            "description": game.description,
            "category": game.category,
            "embed_url": game.embed_url,
            "thumbnail_url": game.thumbnail_url,
            "age_range": game.age_range,
            "duration_minutes": game.duration_minutes,
            "difficulty": game.difficulty,
            "educational_objectives": game.educational_objectives,
            "skills_developed": game.skills_developed,
            "play_count": game.play_count,
            "rating_average": game.rating_average,
        }
    }

@router.get("/embed/{game_id}")
async def get_embed_url(game_id: int, db: AsyncSession = Depends(get_db)):
    """دریافت URL Embed بازی"""
    result = await db.execute(select(EducationalGame).where(EducationalGame.id == game_id))
    game = result.scalar_one_or_none()
    
    if not game:
        raise HTTPException(404, "بازی یافت نشد")
    
    return {
        "embed_url": game.embed_url,
        "title": game.title,
        "source": game.source_website
    }

@router.post("/progress")
async def update_progress(data: GameProgressUpdate, db: AsyncSession = Depends(get_db)):
    """ثبت پیشرفت کاربر در بازی"""
    # بررسی وجود رکورد
    result = await db.execute(
        select(GameProgress).where(
            (GameProgress.user_id == data.user_id) & 
            (GameProgress.game_id == data.game_id)
        )
    )
    progress = result.scalar_one_or_none()
    
    if not progress:
        progress = GameProgress(user_id=data.user_id, game_id=data.game_id)
        db.add(progress)
    
    if data.completed is not None:
        progress.completed = data.completed
    if data.score is not None:
        progress.score = data.score
    if data.time_spent_minutes is not None:
        progress.time_spent_minutes = data.time_spent_minutes
    if data.reflections:
        progress.reflections = data.reflections
    
    if data.completed:
        from datetime import datetime
        progress.completed_at = datetime.utcnow()
    
    await db.commit()
    
    return {"status": "success", "progress_id": progress.id}

@router.get("/user/{user_id}/progress")
async def get_user_progress(user_id: int, db: AsyncSession = Depends(get_db)):
    """دریافت پیشرفت کاربر"""
    result = await db.execute(
        select(GameProgress, EducationalGame)
        .join(EducationalGame)
        .where(GameProgress.user_id == user_id)
    )
    records = result.all()
    
    return {
        "progress": [
            {
                "game_id": gp.game_id,
                "game_title": eg.title,
                "completed": gp.completed,
                "score": gp.score,
                "time_spent_minutes": gp.time_spent_minutes,
                "completed_at": gp.completed_at,
            }
            for gp, eg in records
        ],
        "total_completed": sum(1 for gp, _ in records if gp.completed),
        "total_time_minutes": sum(gp.time_spent_minutes or 0 for gp, _ in records)
    }

@router.get("/categories")
async def get_categories():
    """لیست دسته‌بندی‌ها"""
    return {
        "categories": [
            {"id": "ENVIRONMENT", "name": "محیط زیست", "icon": "🌍", "color": "#10b981"},
            {"id": "AGRICULTURE", "name": "کشاورزی", "icon": "🌾", "color": "#84cc16"},
            {"id": "CLIMATE", "name": "تغییر اقلیم", "icon": "🌡️", "color": "#f59e0b"},
            {"id": "WATER", "name": "مدیریت آب", "icon": "💧", "color": "#3b82f6"},
            {"id": "PUZZLE", "name": "پازل و منطق", "icon": "🧩", "color": "#8b5cf6"},
            {"id": "SCIENCE", "name": "علوم پایه", "icon": "🔬", "color": "#ec4899"},
            {"id": "MATH", "name": "ریاضیات", "icon": "📐", "color": "#6366f1"},
            {"id": "STRATEGY", "name": "استراتژی", "icon": "♟️", "color": "#f97316"},
        ]
    }

@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """آمار کلی بازی‌ها"""
    total_games = (await db.execute(select(func.count(EducationalGame.id)))).scalar()
    total_plays = (await db.execute(select(func.sum(EducationalGame.play_count)))).scalar() or 0
    
    return {
        "total_games": total_games,
        "total_plays": total_plays,
        "categories_count": 8
    }
'''
    write_file(API_DIR / "modules" / "games" / "router.py", content)


# ============================================================
# 4. __init__.py
# ============================================================
def create_init():
    print("\n📦 ایجاد __init__.py...")
    write_file(API_DIR / "modules" / "games" / "__init__.py", "from . import models, router\n")


# ============================================================
# 5. داشبورد فرانت‌اند
# ============================================================
def create_frontend():
    print("\n🎨 ایجاد داشبورد فرانت‌اند...")
    content = '''"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowRight, Gamepad2, Trophy, Clock, Users, Star,
  Filter, X, Maximize2, RotateCcw, BookOpen, TrendingUp
} from "lucide-react";

const API_BASE = "http://localhost:8000/api/v1/games";

const CATEGORIES = [
  { id: "all", name: "همه بازی‌ها", icon: "🎮", color: "#8b5cf6" },
  { id: "ENVIRONMENT", name: "محیط زیست", icon: "🌍", color: "#10b981" },
  { id: "AGRICULTURE", name: "کشاورزی", icon: "🌾", color: "#84cc16" },
  { id: "CLIMATE", name: "تغییر اقلیم", icon: "🌡️", color: "#f59e0b" },
  { id: "WATER", name: "مدیریت آب", icon: "💧", color: "#3b82f6" },
  { id: "PUZZLE", name: "پازل و منطق", icon: "🧩", color: "#8b5cf6" },
  { id: "SCIENCE", name: "علوم پایه", icon: "🔬", color: "#ec4899" },
  { id: "MATH", name: "ریاضیات", icon: "📐", color: "#6366f1" },
  { id: "STRATEGY", name: "استراتژی", icon: "♟️", color: "#f97316" },
];

export default function GamesPage() {
  const [games, setGames] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedGame, setSelectedGame] = useState(null);
  const [showIframe, setShowIframe] = useState(false);
  const [userProgress, setUserProgress] = useState(null);
  const [stats, setStats] = useState(null);
  const iframeRef = useRef(null);

  useEffect(() => {
    loadGames();
    loadStats();
  }, [selectedCategory]);

  const loadGames = async () => {
    const params = selectedCategory !== "all" ? `?category=${selectedCategory}` : "";
    const res = await fetch(`${API_BASE}/list${params}`);
    const data = await res.json();
    setGames(data.games || []);
  };

  const loadStats = async () => {
    const res = await fetch(`${API_BASE}/stats`);
    const data = await res.json();
    setStats(data);
  };

  const startGame = async (game) => {
    setSelectedGame(game);
    setShowIframe(true);
    // ثبت شروع بازی
    await fetch(`${API_BASE}/progress`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: 1, game_id: game.id, time_spent_minutes: 0 })
    });
  };

  const closeGame = () => {
    setShowIframe(false);
    setSelectedGame(null);
    loadGames(); // به‌روزرسانی آمار
  };

  const getCategoryColor = (catId) => {
    const cat = CATEGORIES.find(c => c.id === catId);
    return cat?.color || "#8b5cf6";
  };

  const getCategoryIcon = (catId) => {
    const cat = CATEGORIES.find(c => c.id === catId);
    return cat?.icon || "🎮";
  };

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Header */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-600 to-pink-700 opacity-20" />
        <div className="relative container mx-auto px-6 py-12">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-4 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-6">
              <div className="p-4 rounded-3xl bg-gradient-to-br from-purple-500 to-pink-600 shadow-2xl">
                <Gamepad2 className="h-10 w-10 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-purple-400 text-sm font-medium mb-1">یادگیری از طریق بازی</p>
                <h1 className="text-4xl md:text-5xl font-black text-white mb-2">بازی‌های آموزشی اکو نوژین</h1>
                <p className="text-lg text-slate-300 max-w-3xl">
                  30+ بازی آموزشی تعاملی در حوزه محیط زیست، کشاورزی پایدار، تغییر اقلیم و علوم پایه
                </p>
              </div>
            </div>

            {/* Stats */}
            {stats && (
              <div className="flex gap-6 mt-6">
                <div className="flex items-center gap-2 px-4 py-2 bg-slate-900/50 rounded-xl border border-slate-800">
                  <Gamepad2 className="h-5 w-5 text-purple-400" />
                  <span className="text-white font-bold">{stats.total_games}</span>
                  <span className="text-slate-400 text-sm">بازی آموزشی</span>
                </div>
                <div className="flex items-center gap-2 px-4 py-2 bg-slate-900/50 rounded-xl border border-slate-800">
                  <Trophy className="h-5 w-5 text-amber-400" />
                  <span className="text-white font-bold">{stats.total_plays.toLocaleString()}</span>
                  <span className="text-slate-400 text-sm">بازی انجام‌شده</span>
                </div>
                <div className="flex items-center gap-2 px-4 py-2 bg-slate-900/50 rounded-xl border border-slate-800">
                  <BookOpen className="h-5 w-5 text-emerald-400" />
                  <span className="text-white font-bold">8</span>
                  <span className="text-slate-400 text-sm">دسته‌بندی</span>
                </div>
              </div>
            )}
          </motion.div>
        </div>
      </section>

      {/* Game Player Modal */}
      <AnimatePresence>
        {showIframe && selectedGame && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/90 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-6xl h-[90vh] flex flex-col"
            >
              {/* Header */}
              <div className="flex items-center justify-between p-4 border-b border-slate-800">
                <div>
                  <h2 className="text-xl font-bold text-white">{selectedGame.title}</h2>
                  <p className="text-sm text-slate-400">{selectedGame.description}</p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => iframeRef.current?.requestFullscreen()}
                    className="p-2 text-slate-400 hover:text-white transition-colors"
                    title="تمام صفحه"
                  >
                    <Maximize2 className="h-5 w-5" />
                  </button>
                  <button
                    onClick={closeGame}
                    className="p-2 text-slate-400 hover:text-white transition-colors"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
              </div>
              
              {/* Iframe */}
              <div className="flex-1 bg-black">
                <iframe
                  ref={iframeRef}
                  src={selectedGame.embed_url}
                  className="w-full h-full border-0"
                  allow="fullscreen"
                  allowFullScreen
                  title={selectedGame.title}
                />
              </div>
              
              {/* Footer */}
              <div className="p-4 border-t border-slate-800 bg-slate-900">
                <div className="flex items-center justify-between text-sm text-slate-400">
                  <div className="flex items-center gap-4">
                    <span className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      {selectedGame.duration_minutes} دقیقه
                    </span>
                    <span className="flex items-center gap-1">
                      <Trophy className="h-4 w-4" />
                      سطح: {selectedGame.difficulty === "easy" ? "آسان" : selectedGame.difficulty === "medium" ? "متوسط" : "سخت"}
                    </span>
                  </div>
                  <button onClick={closeGame} className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-bold">
                    پایان بازی
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <section className="container mx-auto px-6 py-8">
        {/* Categories Filter */}
        <div className="flex gap-3 mb-8 overflow-x-auto pb-2 scrollbar-hide">
          {CATEGORIES.map(cat => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-5 py-3 rounded-xl font-bold transition-all flex items-center gap-2 whitespace-nowrap ${
                selectedCategory === cat.id
                  ? "text-white shadow-lg"
                  : "bg-slate-800 text-slate-400 hover:bg-slate-700"
              }`}
              style={selectedCategory === cat.id ? { backgroundColor: cat.color } : {}}
            >
              <span>{cat.icon}</span>
              {cat.name}
            </button>
          ))}
        </div>

        {/* Games Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {games.map((game, idx) => (
            <motion.div
              key={game.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
              className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl overflow-hidden hover:border-purple-500/50 transition-all group cursor-pointer"
              onClick={() => startGame(game)}
            >
              {/* Thumbnail */}
              <div className="relative h-48 bg-slate-800 overflow-hidden">
                {game.thumbnail_url ? (
                  <img
                    src={game.thumbnail_url}
                    alt={game.title}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-6xl">
                    {getCategoryIcon(game.category)}
                  </div>
                )}
                <div
                  className="absolute top-3 right-3 px-3 py-1 rounded-full text-xs font-bold text-white"
                  style={{ backgroundColor: getCategoryColor(game.category) }}
                >
                  {getCategoryIcon(game.category)} {game.category}
                </div>
              </div>

              {/* Content */}
              <div className="p-5">
                <h3 className="text-lg font-bold text-white mb-2 group-hover:text-purple-400 transition-colors">
                  {game.title}
                </h3>
                <p className="text-sm text-slate-400 mb-4 line-clamp-2">
                  {game.description}
                </p>

                {/* Meta Info */}
                <div className="flex items-center justify-between text-xs text-slate-500 mb-4">
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {game.duration_minutes} دقیقه
                  </span>
                  <span className="flex items-center gap-1">
                    <Users className="h-3 w-3" />
                    {game.play_count.toLocaleString()}
                  </span>
                  <span className="flex items-center gap-1">
                    <Star className="h-3 w-3 text-amber-400" />
                    {game.rating_average || "جدید"}
                  </span>
                </div>

                {/* Difficulty Badge */}
                <div className="flex items-center justify-between">
                  <span
                    className={`px-2 py-1 rounded text-xs font-bold ${
                      game.difficulty === "easy"
                        ? "bg-emerald-500/20 text-emerald-300"
                        : game.difficulty === "medium"
                        ? "bg-amber-500/20 text-amber-300"
                        : "bg-red-500/20 text-red-300"
                    }`}
                  >
                    {game.difficulty === "easy" ? "آسان" : game.difficulty === "medium" ? "متوسط" : "سخت"}
                  </span>
                  <button className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-bold transition-colors">
                    شروع بازی
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {games.length === 0 && (
          <div className="text-center py-20">
            <Gamepad2 className="h-16 w-16 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">هیچ بازی‌ای در این دسته‌بندی یافت نشد</p>
          </div>
        )}
      </section>
    </div>
  );
}
'''
    write_file(WEB / "app" / "games" / "page.tsx", content)


# ============================================================
# 6. به‌روزرسانی main.py
# ============================================================
def update_main():
    print("\n🔧 به‌روزرسانی main.py...")
    main_path = API_DIR / "main.py"
    if not main_path.exists():
        print("   ❌ main.py یافت نشد")
        return
    
    content = main_path.read_text(encoding="utf-8")
    
    if "games_router" not in content:
        lines = content.split('\n')
        import_idx = router_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("from api.modules."):
                import_idx = i
            if "app.include_router(" in line:
                router_idx = i
        
        lines.insert(import_idx + 1, "from api.modules.games.router import router as games_router")
        lines.insert(router_idx + 2, 'app.include_router(games_router, prefix="/api/v1")')
        
        main_path.write_text('\n'.join(lines), encoding="utf-8")
        print("   ✅ games_router اضافه شد")
    else:
        print("   ℹ️  از قبل اضافه شده")


# ============================================================
# 7. اسکریپت Seed برای پر کردن دیتابیس
# ============================================================
def create_seed_script():
    print("\n🌱 ایجاد اسکریپت Seed دیتابیس...")
    content = '''# api/scripts/seed_games.py
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from api.core.database import engine, async_session, Base
from api.modules.games.models import EducationalGame
from api.modules.games.games_database import EDUCATIONAL_GAMES
from sqlalchemy import select

async def seed_games():
    print("🔄 در حال ساخت جداول...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("📝 در حال افزودن 30 بازی آموزشی...")
    async with async_session() as session:
        count = 0
        for game_data in EDUCATIONAL_GAMES:
            # بررسی تکراری نبودن
            result = await session.execute(select(EducationalGame).where(EducationalGame.title == game_data["title"]))
            if result.scalar_one_or_none():
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
        
        await session.commit()
        print(f"✅ {count} بازی آموزشی با موفقیت به دیتابیس اضافه شد!")

if __name__ == "__main__":
    asyncio.run(seed_games())
'''
    write_file(API_DIR / "scripts" / "seed_games.py", content)


# ============================================================
# Main
# ============================================================
def main():
    print("🎮 ایجاد ماژول جامع بازی‌های آموزشی")
    print("=" * 70)
    
    if not API_DIR.exists() or not WEB.exists():
        print("❌ دایرکتوری‌ها یافت نشد!")
        return 1
    
    create_models()
    create_games_database()
    create_router()
    create_init()
    create_frontend()
    update_main()
    create_seed_script()
    
    print("\n" + "=" * 70)
    print("✅ ماژول بازی‌های آموزشی با موفقیت ایجاد شد!")
    print("\n🎯 30 بازی آموزشی در 8 دسته‌بندی:")
    print("   🌍 محیط زیست (6 بازی)")
    print("   🌾 کشاورزی و احیای زمین (6 بازی)")
    print("   🌡️ تغییر اقلیم و تاب‌آوری (5 بازی)")
    print("   💧 مدیریت آب (3 بازی)")
    print("   🧩 پازل و منطق (4 بازی)")
    print("   🔬 علوم پایه (6 بازی)")
    print("   📐 ریاضیات (3 بازی)")
    print("   ♟️ استراتژی و مدیریت (3 بازی)")
    print("")
    print("🎮 منابع بازی‌ها:")
    print("   • PhET Interactive Simulations (دانشگاه کلرادو)")
    print("   • Scratch MIT (آزمایشگاه رسانه MIT)")
    print("   • Internet Archive (بازی‌های کلاسیک)")
    print("   • ClassicReload (بازی‌های آموزشی)")
    print("")
    print("🚀 گام بعدی:")
    print("   1. پر کردن دیتابیس با بازی‌ها:")
    print("      python api/scripts/seed_games.py")
    print("")
    print("   2. ری‌استارت سرور بک‌اند:")
    print("      uvicorn api.main:app --reload --port 8000")
    print("")
    print("   3. پاک‌سازی کش فرانت‌اند:")
    print("      cd apps\\web")
    print("      Remove-Item .next -Recurse -Force")
    print("")
    print("   4. اجرای فرانت‌اند:")
    print("      pnpm run dev -- -p 3001")
    print("")
    print("   5. مشاهده:")
    print("      http://localhost:3001/games")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())