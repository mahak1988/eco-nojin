# api/modules/community/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from api.core.database import Base
import enum

class UserRole(enum.Enum):
    FARMER = "farmer"
    EXPERT = "expert"
    RESEARCHER = "researcher"
    MENTOR = "mentor"

class PostType(enum.Enum):
    QUESTION = "question"
    EXPERIENCE = "experience"
    SUCCESS_STORY = "success_story"
    WARNING = "warning"
    RESOURCE_EXCHANGE = "resource_exchange"

class Post(Base):
    __tablename__ = "community_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    post_type = Column(SQLEnum(PostType), nullable=False)
    title = Column(String(500))
    content = Column(Text, nullable=False)
    
    # چندرسانه‌ای
    images = Column(JSON)  # لیست URL تصاویر
    voice_note_url = Column(String(500))  # برای کشاورزانی که تایپ کردن سخت است
    
    # موقعیت جغرافیایی (اختیاری اما تشویق‌شده)
    location_name = Column(String(300))
    latitude = Column(Float)
    longitude = Column(Float)
    
    # دسته‌بندی
    category = Column(String(100))  # irrigation, pest, soil, harvest, etc.
    tags = Column(JSON)
    
    # تعاملات
    view_count = Column(Integer, default=0)
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    is_resolved = Column(Boolean, default=False)  # برای پست‌های از نوع سوال
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    author = relationship("User")
    comments = relationship("Comment", back_populates="post")

class Comment(Base):
    __tablename__ = "community_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("community_posts.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("community_comments.id"))  # برای ریپلای
    
    content = Column(Text, nullable=False)
    voice_note_url = Column(String(500))
    
    upvotes = Column(Integer, default=0)
    is_accepted_answer = Column(Boolean, default=False)
    
    created_at = Column(DateTime, server_default=func.now())
    
    post = relationship("Post", back_populates="comments")
    author = relationship("User")

class UserReputation(Base):
    __tablename__ = "user_reputations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    total_points = Column(Integer, default=0)
    level = Column(String(50), default="novice")  # novice, helper, leading_farmer, wise_elder
    badges = Column(JSON)  # لیست نشان‌ها: ["water_saver", "soil_guardian"]
    
    posts_count = Column(Integer, default=0)
    accepted_answers_count = Column(Integer, default=0)
    
    updated_at = Column(DateTime, onupdate=func.now())

class CommunityEvent(Base):
    __tablename__ = "community_events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    
    event_type = Column(String(50))  # workshop, field_day, online_webinar
    location_name = Column(String(300))
    latitude = Column(Float)
    longitude = Column(Float)
    
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    max_participants = Column(Integer)
    registered_count = Column(Integer, default=0)
    
    organizer_id = Column(Integer, ForeignKey("users.id"))
    cover_image_url = Column(String(500))
    
    created_at = Column(DateTime, server_default=func.now())
