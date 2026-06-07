# api/modules/games/models.py
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
