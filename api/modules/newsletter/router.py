# api/modules/newsletter/router.py
from api.core.schemas import SuccessResponse, IDResponse, StatsResponse, PaginatedResponse
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, field_validator
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.modules.newsletter.models import NewsletterSubscriber, NewsSource
from api.modules.newsletter.rss_service import RSSNewsAggregator

router = APIRouter(prefix="/newsletter", tags=["Newsletter"])


class SubscribeRequest(BaseModel):
    email: str
    full_name: Optional[str] = None
    interests: Optional[List[str]] = []
    language: str = "fa"
    frequency: str = "weekly"
    consent_given: bool = True


class UnsubscribeRequest(BaseModel):
    email: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v or '.' not in v.split('@')[-1]:
            raise ValueError('ایمیل نامعتبر')
        return v.lower().strip()


@router.post("/subscribe", response_model=Dict[str, Any])
async def subscribe(request: SubscribeRequest, db: AsyncSession = Depends(get_db)):
    """عضویت در خبرنامه"""
    # بررسی وجود ایمیل
    result = await db.execute(
        select(NewsletterSubscriber).where(
            NewsletterSubscriber.email == request.email
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        if existing.is_active:
            raise HTTPException(400, "این ایمیل قبلاً در خبرنامه عضو شده است")
        else:
            # فعال‌سازی مجدد
            existing.is_active = True
            existing.unsubscribed_at = None
            await db.commit()
            return {"status": "success", "message": "عضویت شما مجدداً فعال شد"}
    
    # ایجاد عضو جدید
    import secrets
    token = secrets.token_urlsafe(32)
    
    subscriber = NewsletterSubscriber(
        email=request.email,
        full_name=request.full_name,
        interests=request.interests,
        language=request.language,
        frequency=request.frequency,
        is_verified=False,
        verification_token=token,
        consent_given=request.consent_given,
        consent_date=datetime.utcnow()
    )
    
    db.add(subscriber)
    await db.commit()
    
    # TODO: ارسال ایمیل تأیید
    
    return {
        "status": "success",
        "message": "عضویت شما با موفقیت ثبت شد. لطفاً ایمیل خود را تأیید کنید.",
        "subscriber_id": subscriber.id
    }


@router.post("/unsubscribe", response_model=Dict[str, Any])
async def unsubscribe(request: UnsubscribeRequest, db: AsyncSession = Depends(get_db)):
    """لغو عضویت از خبرنامه"""
    result = await db.execute(
        select(NewsletterSubscriber).where(
            NewsletterSubscriber.email == request.email
        )
    )
    subscriber = result.scalar_one_or_none()
    
    if not subscriber:
        raise HTTPException(404, "این ایمیل در خبرنامه عضو نیست")
    
    subscriber.is_active = False
    subscriber.unsubscribed_at = datetime.utcnow()
    await db.commit()
    
    return {"status": "success", "message": "لغو عضویت با موفقیت انجام شد"}


@router.get("/news", response_model=Dict[str, Any])
async def get_news(
    category: Optional[str] = None,
    limit: int = Query(50, le=100)
):
    """دریافت آخرین اخبار از منابع معتبر"""
    articles = await RSSNewsAggregator.fetch_all_news(category=category, limit=limit)
    
    return {
        "articles": articles,
        "total": len(articles),
        "sources_count": len(RSSNewsAggregator.NEWS_SOURCES)
    }


@router.get("/sources", response_model=Dict[str, Any])
async def get_sources(category: Optional[str] = None):
    """دریافت لیست منابع خبری"""
    sources = RSSNewsAggregator.get_sources(category=category)
    
    return {
        "sources": sources,
        "total": len(sources)
    }


@router.get("/categories", response_model=Dict[str, Any])
async def get_categories():
    """دریافت دسته‌بندی‌های خبری"""
    return {
        "categories": [
            {"id": "agriculture", "name": "کشاورزی پایدار", "icon": "🌾", "color": "#10b981"},
            {"id": "climate", "name": "تغییر اقلیم", "icon": "🌡️", "color": "#f59e0b"},
            {"id": "environment", "name": "محیط زیست", "icon": "🌍", "color": "#3b82f6"},
            {"id": "water", "name": "مدیریت آب", "icon": "💧", "color": "#06b6d4"},
            {"id": "research", "name": "تحقیقات علمی", "icon": "🔬", "color": "#8b5cf6"},
            {"id": "development", "name": "توسعه بین‌المللی", "icon": "🌐", "color": "#ec4899"},
        ]
    }


@router.get("/stats", response_model=Dict[str, Any])
async def get_stats(db: AsyncSession = Depends(get_db)):
    """آمار خبرنامه"""
    from sqlalchemy import func
    
    total_subscribers = (await db.execute(
        select(func.count(NewsletterSubscriber.id)).where(
            NewsletterSubscriber.is_active == True
        )
    )).scalar() or 0
    
    return {
        "total_subscribers": total_subscribers,
        "total_sources": len(RSSNewsAggregator.NEWS_SOURCES),
        "categories_count": 6
    }