# api/modules/newsletter/models.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text
from sqlalchemy.sql import func
from api.core.database import Base


class NewsletterSubscriber(Base):
    """مشترکان خبرنامه"""
    __tablename__ = "newsletter_subscribers"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    full_name = Column(String(200))
    
    # ترجیحات
    interests = Column(JSON)  # ["agriculture", "climate", "water", etc.]
    language = Column(String(10), default="fa")
    frequency = Column(String(20), default="weekly")  # daily, weekly, monthly
    
    # وضعیت
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(100))
    
    # آمار
    subscribed_at = Column(DateTime, server_default=func.now())
    last_email_sent = Column(DateTime)
    emails_received = Column(Integer, default=0)
    emails_opened = Column(Integer, default=0)
    
    # GDPR
    consent_given = Column(Boolean, default=False)
    consent_date = Column(DateTime)
    
    unsubscribed_at = Column(DateTime)


class NewsSource(Base):
    """منابع خبری"""
    __tablename__ = "news_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    name_en = Column(String(200))
    
    # اطلاعات فنی
    rss_url = Column(String(500))
    website_url = Column(String(500))
    logo_url = Column(String(500))
    
    # دسته‌بندی
    category = Column(String(100))  # agriculture, climate, water, etc.
    language = Column(String(10), default="en")
    country = Column(String(100))
    
    # وضعیت
    is_active = Column(Boolean, default=True)
    fetch_frequency = Column(Integer, default=3600)  # seconds
    
    # آمار
    last_fetched = Column(DateTime)
    articles_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, server_default=func.now())


class NewsArticle(Base):
    """مقالات خبری"""
    __tablename__ = "news_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, nullable=False)
    
    # اطلاعات مقاله
    title = Column(String(500), nullable=False)
    title_en = Column(String(500))
    summary = Column(Text)
    content = Column(Text)
    
    # لینک‌ها
    url = Column(String(500), nullable=False)
    image_url = Column(String(500))
    
    # متادیتا
    author = Column(String(200))
    published_at = Column(DateTime)
    category = Column(String(100))
    tags = Column(JSON)
    
    # زبان
    language = Column(String(10), default="en")
    
    # آمار
    view_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, server_default=func.now())


class NewsletterCampaign(Base):
    """کمپین‌های خبرنامه"""
    __tablename__ = "newsletter_campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    subject = Column(String(500), nullable=False)
    
    # محتوا
    content_html = Column(Text)
    content_text = Column(Text)
    
    # هدف‌گیری
    target_segments = Column(JSON)  # ["all", "agriculture", "climate", etc.]
    
    # وضعیت
    status = Column(String(50), default="draft")  # draft, scheduled, sent, cancelled
    scheduled_at = Column(DateTime)
    sent_at = Column(DateTime)
    
    # آمار
    total_recipients = Column(Integer, default=0)
    emails_sent = Column(Integer, default=0)
    emails_opened = Column(Integer, default=0)
    emails_clicked = Column(Integer, default=0)
    
    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(Integer)