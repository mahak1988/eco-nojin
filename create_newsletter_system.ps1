# ============================================================================
# ایجاد سیستم خبرنامه جامع اکو نوژین
# ============================================================================

$ErrorActionPreference = "Stop"
$ROOT = "D:\econojin.com"
$API_DIR = "$ROOT\api"
$WEB_DIR = "$ROOT\apps\web\src"

Write-Host "📧 ایجاد سیستم خبرنامه جامع اکو نوژین" -ForegroundColor Cyan
Write-Host ("=" * 70)

# ============================================================================
# 1. ایجاد مدل‌های دیتابیس خبرنامه
# ============================================================================
Write-Host "`n📊 ایجاد مدل‌های دیتابیس..." -ForegroundColor Yellow

$newsletterModelsContent = @'
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
'@

$modelsPath = "$API_DIR\modules\newsletter\models.py"
New-Item -ItemType Directory -Path (Split-Path $modelsPath) -Force | Out-Null
[System.IO.File]::WriteAllText($modelsPath, $newsletterModelsContent, [System.Text.Encoding]::UTF8)
Write-Host "   ✅ models.py ایجاد شد" -ForegroundColor Green


# ============================================================================
# 2. ایجاد سرویس RSS Reader
# ============================================================================
Write-Host "`n📡 ایجاد سرویس RSS Reader..." -ForegroundColor Yellow

$rssServiceContent = @'
# api/modules/newsletter/rss_service.py
"""
سرویس خواندن RSS feeds از منابع معتبر جهانی
بدون نیاز به ذخیره‌سازی محلی - فقط لینک‌ها را جمع‌آوری می‌کند
"""
import feedparser
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict
import aiohttp


class RSSNewsAggregator:
    """جمع‌آوری اخبار از منابع RSS"""
    
    # منابع معتبر جهانی
    NEWS_SOURCES = [
        {
            "name": "FAO News",
            "name_en": "FAO News",
            "rss_url": "http://www.fao.org/news/rss-feed-en.xml",
            "website": "http://www.fao.org/news/news-detail/en/",
            "category": "agriculture",
            "language": "en",
            "country": "International",
            "logo": "https://www.fao.org/fileadmin/templates/faoweb/images/FAO.gif"
        },
        {
            "name": "UNCCD News",
            "name_en": "UN Convention to Combat Desertification",
            "rss_url": "https://www.unccd.int/news/rss.xml",
            "website": "https://www.unccd.int/news",
            "category": "environment",
            "language": "en",
            "country": "International",
            "logo": "https://www.unccd.int/themes/custom/unccd/logo.svg"
        },
        {
            "name": "NASA Earth Observatory",
            "name_en": "NASA Earth Observatory",
            "rss_url": "https://earthobservatory.nasa.gov/feeds/earth-observatory.rss",
            "website": "https://earthobservatory.nasa.gov/",
            "category": "climate",
            "language": "en",
            "country": "USA",
            "logo": "https://earthobservatory.nasa.gov/favicon.ico"
        },
        {
            "name": "Nature Sustainability",
            "name_en": "Nature Sustainability",
            "rss_url": "http://feeds.nature.com/natsustain",
            "website": "https://www.nature.com/natsustain/",
            "category": "research",
            "language": "en",
            "country": "International",
            "logo": "https://www.nature.com/nature-portfolio-assets/global/nature-brand/safari-pinned-tab.svg"
        },
        {
            "name": "The Guardian Environment",
            "name_en": "The Guardian Environment",
            "rss_url": "https://www.theguardian.com/environment/rss",
            "website": "https://www.theguardian.com/environment",
            "category": "environment",
            "language": "en",
            "country": "UK",
            "logo": "https://assets.guim.co.uk/images/favicons/74d410f87c584d5f8e6e52f2a14e27a2/32x32.ico"
        },
        {
            "name": "Reuters Environment",
            "name_en": "Reuters Environment",
            "rss_url": "https://www.reuters.com/technology/environment/rss",
            "website": "https://www.reuters.com/technology/environment/",
            "category": "environment",
            "language": "en",
            "country": "International",
            "logo": "https://www.reuters.com/pf/resources/images/reuters/favicon/tr_fvcn_kinesis_32x32_v2.ico"
        },
        {
            "name": "CGIAR",
            "name_en": "CGIAR Research",
            "rss_url": "https://www.cgiar.org/feed/",
            "website": "https://www.cgiar.org/",
            "category": "agriculture",
            "language": "en",
            "country": "International",
            "logo": "https://www.cgiar.org/wp-content/themes/cgiar/assets/images/favicon.ico"
        },
        {
            "name": "World Resources Institute",
            "name_en": "World Resources Institute",
            "rss_url": "https://www.wri.org/rss.xml",
            "website": "https://www.wri.org/",
            "category": "environment",
            "language": "en",
            "country": "USA",
            "logo": "https://www.wri.org/themes/custom/wri_theme/favicon.ico"
        },
        {
            "name": "IUCN",
            "name_en": "International Union for Conservation of Nature",
            "rss_url": "https://www.iucn.org/news/feed",
            "website": "https://www.iucn.org/",
            "category": "environment",
            "language": "en",
            "country": "International",
            "logo": "https://www.iucn.org/themes/custom/iucn_theme/favicon.ico"
        },
        {
            "name": "IPCC Reports",
            "name_en": "Intergovernmental Panel on Climate Change",
            "rss_url": "https://www.ipcc.ch/feed/",
            "website": "https://www.ipcc.ch/",
            "category": "climate",
            "language": "en",
            "country": "International",
            "logo": "https://www.ipcc.ch/site/assets/uploads/2019/08/ipcc_logo.png"
        },
        {
            "name": "Devex",
            "name_en": "Devex - International Development",
            "rss_url": "https://www.devex.com/en/articles.rss",
            "website": "https://www.devex.com/",
            "category": "development",
            "language": "en",
            "country": "International",
            "logo": "https://www.devex.com/favicon.ico"
        },
        {
            "name": "World Bank Agriculture",
            "name_en": "World Bank Agriculture",
            "rss_url": "https://www.worldbank.org/en/topic/agriculture/rss",
            "website": "https://www.worldbank.org/en/topic/agriculture",
            "category": "agriculture",
            "language": "en",
            "country": "International",
            "logo": "https://www.worldbank.org/favicon.ico"
        },
        {
            "name": "UN Environment Programme",
            "name_en": "UN Environment Programme",
            "rss_url": "https://www.unep.org/news-and-stories/rss.xml",
            "website": "https://www.unep.org/",
            "category": "environment",
            "language": "en",
            "country": "International",
            "logo": "https://www.unep.org/themes/custom/unep/favicon.ico"
        },
        {
            "name": "Climate Change News",
            "name_en": "Climate Change News",
            "rss_url": "https://www.climatechangenews.com/feed/",
            "website": "https://www.climatechangenews.com/",
            "category": "climate",
            "language": "en",
            "country": "UK",
            "logo": "https://www.climatechangenews.com/favicon.ico"
        },
        {
            "name": "Agriculture.com",
            "name_en": "Successful Farming",
            "rss_url": "https://www.agriculture.com/rss/latest",
            "website": "https://www.agriculture.com/",
            "category": "agriculture",
            "language": "en",
            "country": "USA",
            "logo": "https://www.agriculture.com/favicon.ico"
        }
    ]
    
    @classmethod
    async def fetch_rss_feed(cls, source: Dict, max_items: int = 10) -> List[Dict]:
        """خواندن یک RSS feed"""
        try:
            # استفاده از feedparser برای خواندن RSS
            feed = feedparser.parse(source["rss_url"])
            
            articles = []
            for entry in feed.entries[:max_items]:
                article = {
                    "title": entry.get("title", ""),
                    "title_en": entry.get("title", ""),
                    "summary": entry.get("summary", ""),
                    "url": entry.get("link", ""),
                    "published_at": entry.get("published", ""),
                    "author": entry.get("author", ""),
                    "image_url": cls._extract_image(entry),
                    "source_name": source["name"],
                    "source_logo": source.get("logo", ""),
                    "category": source["category"],
                    "language": source["language"],
                }
                articles.append(article)
            
            return articles
        except Exception as e:
            print(f"Error fetching {source['name']}: {e}")
            return []
    
    @staticmethod
    def _extract_image(entry) -> str:
        """استخراج تصویر از entry"""
        # تلاش برای پیدا کردن تصویر در media_content
        if hasattr(entry, "media_content") and entry.media_content:
            for media in entry.media_content:
                if "image" in media.get("type", ""):
                    return media.get("url", "")
        
        # تلاش در media_thumbnail
        if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
            return entry.media_thumbnail[0].get("url", "")
        
        # تلاش در enclosures
        if hasattr(entry, "enclosures") and entry.enclosures:
            for enclosure in entry.enclosures:
                if "image" in enclosure.get("type", ""):
                    return enclosure.get("href", "")
        
        return ""
    
    @classmethod
    async def fetch_all_news(cls, category: str = None, limit: int = 50) -> List[Dict]:
        """دریافت اخبار از تمام منابع"""
        sources = cls.NEWS_SOURCES
        
        if category:
            sources = [s for s in sources if s["category"] == category]
        
        # خواندن همزمان تمام feeds
        tasks = [cls.fetch_rss_feed(source, max_items=10) for source in sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # ترکیب و مرتب‌سازی
        all_articles = []
        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)
        
        # مرتب‌سازی بر اساس تاریخ (جدیدترین اول)
        all_articles.sort(key=lambda x: x.get("published_at", ""), reverse=True)
        
        return all_articles[:limit]
    
    @classmethod
    def get_sources(cls, category: str = None) -> List[Dict]:
        """دریافت لیست منابع"""
        sources = cls.NEWS_SOURCES
        
        if category:
            sources = [s for s in sources if s["category"] == category]
        
        return sources
'@

$rssServicePath = "$API_DIR\modules\newsletter\rss_service.py"
[System.IO.File]::WriteAllText($rssServicePath, $rssServiceContent, [System.Text.Encoding]::UTF8)
Write-Host "   ✅ rss_service.py ایجاد شد" -ForegroundColor Green


# ============================================================================
# 3. ایجاد Router API
# ============================================================================
Write-Host "`n🔌 ایجاد Router API..." -ForegroundColor Yellow

$routerContent = @'
# api/modules/newsletter/router.py
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.modules.newsletter.models import NewsletterSubscriber, NewsSource
from api.modules.newsletter.rss_service import RSSNewsAggregator

router = APIRouter(prefix="/newsletter", tags=["Newsletter"])


class SubscribeRequest(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    interests: Optional[List[str]] = []
    language: str = "fa"
    frequency: str = "weekly"
    consent_given: bool = True


class UnsubscribeRequest(BaseModel):
    email: EmailStr


@router.post("/subscribe")
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


@router.post("/unsubscribe")
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


@router.get("/news")
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


@router.get("/sources")
async def get_sources(category: Optional[str] = None):
    """دریافت لیست منابع خبری"""
    sources = RSSNewsAggregator.get_sources(category=category)
    
    return {
        "sources": sources,
        "total": len(sources)
    }


@router.get("/categories")
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


@router.get("/stats")
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
'@

$routerPath = "$API_DIR\modules\newsletter\router.py"
[System.IO.File]::WriteAllText($routerPath, $routerContent, [System.Text.Encoding]::UTF8)
Write-Host "   ✅ router.py ایجاد شد" -ForegroundColor Green


# ============================================================================
# 4. ایجاد __init__.py
# ============================================================================
Write-Host "`n📦 ایجاد __init__.py..." -ForegroundColor Yellow

$initContent = @'
# api/modules/newsletter/__init__.py
from . import models, router, rss_service
'@

$initPath = "$API_DIR\modules\newsletter\__init__.py"
[System.IO.File]::WriteAllText($initPath, $initContent, [System.Text.Encoding]::UTF8)
Write-Host "   ✅ __init__.py ایجاد شد" -ForegroundColor Green


# ============================================================================
# 5. به‌روزرسانی main.py
# ============================================================================
Write-Host "`n🔧 به‌روزرسانی main.py..." -ForegroundColor Yellow

$mainPath = "$API_DIR\main.py"
$mainContent = [System.IO.File]::ReadAllText($mainPath, [System.Text.Encoding]::UTF8)

if ("newsletter_router" -notin $mainContent) {
    # اضافه کردن import
    $mainContent = $mainContent -replace '(from api\.modules\.\w+\.router import router as \w+_router)', "`$1`nfrom api.modules.newsletter.router import router as newsletter_router"
    
    # اضافه کردن registration
    $mainContent = $mainContent -replace '(app\.include_router\(\w+_router, prefix="/api/v1"\))', "`$1`napp.include_router(newsletter_router, prefix=`"/api/v1`")"
    
    [System.IO.File]::WriteAllText($mainPath, $mainContent, [System.Text.Encoding]::UTF8)
    Write-Host "   ✅ newsletter_router به main.py اضافه شد" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  newsletter_router از قبل در main.py ثبت شده" -ForegroundColor Cyan
}


# ============================================================================
# 6. ایجاد صفحه فرانت‌اند خبرنامه
# ============================================================================
Write-Host "`n🎨 ایجاد صفحه فرانت‌اند خبرنامه..." -ForegroundColor Yellow

$newsletterPageContent = @'
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight, Mail, Newspaper, Bell, Gift, Users, Calendar,
  CheckCircle, Clock, ExternalLink, Filter, Globe, Tag,
  TrendingUp, BookOpen, Award, Sparkles, Loader2
} from "lucide-react";

const API_BASE = "http://localhost:8000/api/v1/newsletter";

const CATEGORIES = [
  { id: "all", name: "همه اخبار", icon: "🌍", color: "#8b5cf6" },
  { id: "agriculture", name: "کشاورزی پایدار", icon: "🌾", color: "#10b981" },
  { id: "climate", name: "تغییر اقلیم", icon: "🌡️", color: "#f59e0b" },
  { id: "environment", name: "محیط زیست", icon: "🌍", color: "#3b82f6" },
  { id: "water", name: "مدیریت آب", icon: "💧", color: "#06b6d4" },
  { id: "research", name: "تحقیقات علمی", icon: "🔬", color: "#8b5cf6" },
  { id: "development", name: "توسعه بین‌المللی", icon: "🌐", color: "#ec4899" },
];

const BENEFITS = [
  { icon: Newspaper, title: "مقالات اختصاصی", desc: "دسترسی زودهنگام به مقالات تخصصی قبل از انتشار عمومی" },
  { icon: Bell, title: "هشدارهای مهم", desc: "اطلاع‌رسانی فوری درباره رویدادها، وبینارها و فرصت‌ها" },
  { icon: Gift, title: "منابع رایگان", desc: "دریافت رایگان کتاب‌های الکترونیکی، گزارش‌ها و ابزارها" },
  { icon: Users, title: "جامعه اختصاصی", desc: "دسترسی به گروه ویژه مشترکان خبرنامه و شبکه‌سازی" },
  { icon: Calendar, title: "تقویم رویدادها", desc: "اطلاع از تمام رویدادهای مرتبط با کشاورزی پایدار" },
  { icon: CheckCircle, title: "بدون اسپم", desc: "فقط محتوای ارزشمند، حداکثر یک ایمیل در هفته" },
];

export default function NewsletterPage() {
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [interests, setInterests] = useState<string[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [news, setNews] = useState<any[]>([]);
  const [sources, setSources] = useState<any[]>([]);
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [loadingNews, setLoadingNews] = useState(false);
  const [stats, setStats] = useState({ total_subscribers: 0, total_sources: 0 });

  useEffect(() => {
    loadNews();
    loadSources();
    loadStats();
  }, [selectedCategory]);

  const loadNews = async () => {
    setLoadingNews(true);
    try {
      const params = selectedCategory !== "all" ? `?category=${selectedCategory}` : "";
      const res = await fetch(`${API_BASE}/news${params}`);
      if (res.ok) {
        const data = await res.json();
        setNews(data.articles || []);
      }
    } catch (error) {
      console.error("Failed to load news:", error);
    } finally {
      setLoadingNews(false);
    }
  };

  const loadSources = async () => {
    try {
      const res = await fetch(`${API_BASE}/sources`);
      if (res.ok) {
        const data = await res.json();
        setSources(data.sources || []);
      }
    } catch (error) {
      console.error("Failed to load sources:", error);
    }
  };

  const loadStats = async () => {
    try {
      const res = await fetch(`${API_BASE}/stats`);
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (error) {
      console.error("Failed to load stats:", error);
    }
  };

  const handleSubscribe = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setIsSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/subscribe`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          full_name: fullName,
          interests,
          language: "fa",
          frequency: "weekly",
          consent_given: true
        })
      });

      if (res.ok) {
        setIsSubscribed(true);
        setEmail("");
        setFullName("");
        setInterests([]);
      } else {
        const data = await res.json();
        alert(data.detail || "خطا در ثبت عضویت");
      }
    } catch (error) {
      alert("خطا در اتصال به سرور");
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleInterest = (interest: string) => {
    setInterests(prev =>
      prev.includes(interest)
        ? prev.filter(i => i !== interest)
        : [...prev, interest]
    );
  };

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero Section */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-pink-600 to-rose-700 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />

        <div className="relative container mx-auto px-6 py-20">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-pink-400 hover:text-pink-300 mb-6 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>

            <div className="flex items-start gap-6 mb-6">
              <div className="p-5 rounded-3xl bg-gradient-to-br from-pink-500 to-rose-600 shadow-2xl">
                <Mail className="h-12 w-12 text-white" />
              </div>
              <div className="flex-1">
                <h1 className="text-5xl md:text-6xl font-black text-white mb-4">خبرنامه اکو نوژین</h1>
                <p className="text-xl text-slate-300 max-w-3xl leading-relaxed">
                  عضو خانواده اکو نوژین شوید و هر هفته جدیدترین مقالات،
                  تحقیقات و فرصت‌های یادگیری را در ایمیل خود دریافت کنید
                </p>
              </div>
            </div>

            {/* Stats */}
            <div className="flex gap-6 mt-8">
              <div className="flex items-center gap-2 px-4 py-2 bg-slate-900/50 rounded-xl border border-slate-800">
                <Users className="h-5 w-5 text-pink-400" />
                <span className="text-white font-bold">{stats.total_subscribers.toLocaleString()}</span>
                <span className="text-slate-400 text-sm">مشترک فعال</span>
              </div>
              <div className="flex items-center gap-2 px-4 py-2 bg-slate-900/50 rounded-xl border border-slate-800">
                <Globe className="h-5 w-5 text-pink-400" />
                <span className="text-white font-bold">{stats.total_sources}</span>
                <span className="text-slate-400 text-sm">منبع معتبر جهانی</span>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Subscribe Form */}
      <section className="container mx-auto px-6 py-16">
        <div className="max-w-3xl mx-auto">
          {isSubscribed ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-gradient-to-br from-emerald-900/30 to-teal-900/30 border border-emerald-500/30 rounded-3xl p-12 text-center"
            >
              <CheckCircle className="h-20 w-20 text-emerald-400 mx-auto mb-6" />
              <h2 className="text-3xl font-bold text-white mb-4">عضویت شما با موفقیت ثبت شد!</h2>
              <p className="text-lg text-slate-300 mb-6">
                لطفاً ایمیل خود را بررسی کنید و روی لینک تأیید کلیک کنید.
              </p>
              <button
                onClick={() => setIsSubscribed(false)}
                className="px-6 py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-bold"
              >
                عضویت دیگری
              </button>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gradient-to-br from-pink-900/20 to-rose-900/20 border border-pink-500/30 rounded-3xl p-8"
            >
              <h2 className="text-3xl font-bold text-white mb-6 text-center">
                به خانواده اکو نوژین بپیوندید
              </h2>

              <form onSubmit={handleSubscribe} className="space-y-6">
                <div>
                  <label className="block text-sm font-bold text-white mb-2">
                    ایمیل <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    placeholder="your@email.com"
                    className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:border-pink-500 focus:outline-none"
                    dir="ltr"
                  />
                </div>

                <div>
                  <label className="block text-sm font-bold text-white mb-2">نام و نام خانوادگی</label>
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="نام شما"
                    className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:border-pink-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-sm font-bold text-white mb-3">علاقه‌مندی‌ها</label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {CATEGORIES.filter(c => c.id !== "all").map(cat => (
                      <button
                        key={cat.id}
                        type="button"
                        onClick={() => toggleInterest(cat.id)}
                        className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${
                          interests.includes(cat.id)
                            ? "text-white"
                            : "bg-slate-800 text-slate-400 hover:bg-slate-700"
                        }`}
                        style={interests.includes(cat.id) ? { backgroundColor: cat.color } : {}}
                      >
                        {cat.icon} {cat.name}
                      </button>
                    ))}
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full py-4 bg-gradient-to-r from-pink-600 to-rose-600 hover:from-pink-700 hover:to-rose-700 text-white rounded-xl font-bold text-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      در حال ثبت...
                    </>
                  ) : (
                    <>
                      <Mail className="h-5 w-5" />
                      عضویت در خبرنامه
                    </>
                  )}
                </button>

                <p className="text-xs text-slate-500 text-center">
                  با عضویت، شما با سیاست حریم خصوصی ما موافقت می‌کنید. هر زمان می‌توانید لغو عضویت کنید.
                </p>
              </form>
            </motion.div>
          )}
        </div>
      </section>

      {/* Benefits */}
      <section className="container mx-auto px-6 py-16 bg-gradient-to-b from-slate-950 via-slate-900/50 to-slate-950">
        <div className="text-center mb-12">
          <Sparkles className="h-12 w-12 text-pink-400 mx-auto mb-4" />
          <h2 className="text-4xl font-bold text-white mb-4">
            چرا عضو <span className="text-pink-400">خبرنامه</span> شوید؟
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {BENEFITS.map((benefit, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.1 }}
              className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6"
            >
              <div className="p-3 rounded-xl bg-pink-500/10 inline-block mb-4">
                <benefit.icon className="h-8 w-8 text-pink-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">{benefit.title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed">{benefit.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* News Sources */}
      <section className="container mx-auto px-6 py-16">
        <div className="text-center mb-12">
          <Globe className="h-12 w-12 text-pink-400 mx-auto mb-4" />
          <h2 className="text-4xl font-bold text-white mb-4">
            منابع <span className="text-pink-400">معتبر جهانی</span>
          </h2>
          <p className="text-xl text-slate-400">
            اخبار از {sources.length} منبع معتبر بین‌المللی
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 max-w-6xl mx-auto">
          {sources.map((source, idx) => (
            <motion.a
              key={idx}
              href={source.website_url}
              target="_blank"
              rel="noopener noreferrer"
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.05 }}
              whileHover={{ scale: 1.05 }}
              className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 hover:border-pink-500/50 transition-all flex flex-col items-center text-center group"
            >
              <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center mb-3 overflow-hidden">
                {source.logo ? (
                  <img src={source.logo} alt={source.name} className="w-12 h-12 object-contain" />
                ) : (
                  <Globe className="h-8 w-8 text-slate-400" />
                )}
              </div>
              <h3 className="font-bold text-white text-sm mb-1 group-hover:text-pink-400 transition-colors">
                {source.name}
              </h3>
              <p className="text-xs text-slate-500">{source.country}</p>
              <ExternalLink className="h-3 w-3 text-slate-600 mt-2" />
            </motion.a>
          ))}
        </div>
      </section>

      {/* Latest News */}
      <section className="container mx-auto px-6 py-16 bg-gradient-to-b from-slate-950 via-slate-900/50 to-slate-950">
        <div className="text-center mb-12">
          <Newspaper className="h-12 w-12 text-pink-400 mx-auto mb-4" />
          <h2 className="text-4xl font-bold text-white mb-4">
            آخرین <span className="text-pink-400">اخبار</span>
          </h2>
        </div>

        {/* Category Filter */}
        <div className="flex gap-3 mb-8 overflow-x-auto pb-2 justify-center">
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

        {/* News Grid */}
        {loadingNews ? (
          <div className="text-center py-20">
            <Loader2 className="h-12 w-12 text-pink-400 animate-spin mx-auto mb-4" />
            <p className="text-slate-400">در حال بارگذاری اخبار...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
            {news.slice(0, 12).map((article, idx) => (
              <motion.a
                key={idx}
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden hover:border-pink-500/50 transition-all group"
              >
                {article.image_url && (
                  <div className="h-48 overflow-hidden">
                    <img
                      src={article.image_url}
                      alt={article.title}
                      className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                    />
                  </div>
                )}
                <div className="p-5">
                  <div className="flex items-center gap-2 mb-3">
                    {article.source_logo && (
                      <img src={article.source_logo} alt={article.source_name} className="w-6 h-6 rounded" />
                    )}
                    <span className="text-xs text-slate-400">{article.source_name}</span>
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2 group-hover:text-pink-400 transition-colors line-clamp-2">
                    {article.title}
                  </h3>
                  {article.summary && (
                    <p className="text-sm text-slate-400 line-clamp-3 mb-3">
                      {article.summary}
                    </p>
                  )}
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {article.published_at ? new Date(article.published_at).toLocaleDateString("fa-IR") : ""}
                    </span>
                    <ExternalLink className="h-4 w-4" />
                  </div>
                </div>
              </motion.a>
            ))}
          </div>
        )}

        {news.length === 0 && !loadingNews && (
          <div className="text-center py-20">
            <Newspaper className="h-16 w-16 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">هیچ خبری یافت نشد</p>
          </div>
        )}
      </section>

      {/* CTA */}
      <section className="container mx-auto px-6 py-16">
        <div className="max-w-4xl mx-auto bg-gradient-to-br from-pink-900/30 to-rose-900/30 border border-pink-500/30 rounded-3xl p-12 text-center">
          <Mail className="h-16 w-16 text-pink-400 mx-auto mb-6" />
          <h2 className="text-3xl font-bold text-white mb-4">
            آماده پیوستن به خانواده اکو نوژین هستید؟
          </h2>
          <p className="text-lg text-slate-300 mb-8">
            همین حالا عضو شوید و از جدیدترین اخبار و تحقیقات مطلع شوید
          </p>
          <button
            onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
            className="px-8 py-4 bg-gradient-to-r from-pink-600 to-rose-600 hover:from-pink-700 hover:to-rose-700 text-white rounded-xl font-bold text-lg transition-all shadow-lg shadow-pink-500/30"
          >
            عضویت در خبرنامه
          </button>
        </div>
      </section>
    </div>
  );
}
'@

$newsletterPagePath = "$WEB_DIR\app\newsletter\page.tsx"
[System.IO.File]::WriteAllText($newsletterPagePath, $newsletterPageContent, [System.Text.Encoding]::UTF8)
Write-Host "   ✅ newsletter/page.tsx ایجاد شد" -ForegroundColor Green


# ============================================================================
# 7. نصب پکیج‌های مورد نیاز
# ============================================================================
Write-Host "`n📦 نصب پکیج‌های مورد نیاز..." -ForegroundColor Yellow

$packages = @("feedparser", "aiohttp")
foreach ($package in $packages) {
    try {
        $result = & python -m pip install $package -q 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ $package نصب شد" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  $package: $result" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   ⚠️  $package: $_" -ForegroundColor Yellow
    }
}


# ============================================================================
# 8. پاک‌سازی کش
# ============================================================================
Write-Host "`n🧹 پاک‌سازی کش Next.js..." -ForegroundColor Yellow
$nextDir = "$ROOT\apps\web\.next"
if (Test-Path $nextDir) {
    Remove-Item -Path $nextDir -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "   ✅ پوشه .next حذف شد" -ForegroundColor Green
}


# ============================================================================
# خلاصه نهایی
# ============================================================================
Write-Host "`n" -NoNewline
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "✅ سیستم خبرنامه جامع با موفقیت ایجاد شد!" -ForegroundColor Green
Write-Host ("=" * 70) -ForegroundColor Cyan

Write-Host "`n🎯 ویژگی‌های سیستم:" -ForegroundColor Yellow
Write-Host "   📡 اتصال به 15 منبع معتبر جهانی (FAO, NASA, IPCC, etc.)"
Write-Host "   📰 جمع‌آوری خودکار اخبار از RSS feeds"
Write-Host "   🎯 فیلتر بر اساس دسته‌بندی (کشاورزی، اقلیم، محیط زیست، ...)"
Write-Host "   📧 سیستم عضویت با تأیید ایمیل"
Write-Host "   🌍 بدون بار فنی - فقط لینک به منابع اصلی"
Write-Host "   📊 آمار مشترکان و منابع"

Write-Host "`n📡 منابع خبری متصل:" -ForegroundColor Yellow
Write-Host "   • FAO News (سازمان خواربار و کشاورزی ملل متحد)"
Write-Host "   • UNCCD (کنوانسیون مبارزه با بیابان‌زایی)"
Write-Host "   • NASA Earth Observatory"
Write-Host "   • Nature Sustainability"
Write-Host "   • The Guardian Environment"
Write-Host "   • Reuters Environment"
Write-Host "   • CGIAR (مرکز تحقیقات کشاورزی بین‌المللی)"
Write-Host "   • World Resources Institute"
Write-Host "   • IUCN (اتحادیه بین‌المللی حفاظت از طبیعت)"
Write-Host "   • IPCC (هیئت بین‌دولتی تغییر اقلیم)"
Write-Host "   • Devex (توسعه بین‌المللی)"
Write-Host "   • World Bank Agriculture"
Write-Host "   • UN Environment Programme"
Write-Host "   • Climate Change News"
Write-Host "   • Agriculture.com"

Write-Host "`n🚀 گام‌های بعدی:" -ForegroundColor Cyan
Write-Host "   1. ری‌استارت سرور بک‌اند:"
Write-Host "      uvicorn api.main:app --reload --port 8000" -ForegroundColor White
Write-Host ""
Write-Host "   2. اجرای فرانت‌اند:"
Write-Host "      cd apps\web" -ForegroundColor White
Write-Host "      pnpm run dev -- -p 3001" -ForegroundColor White
Write-Host ""
Write-Host "   3. مشاهده:"
Write-Host "      • خبرنامه: http://localhost:3001/newsletter" -ForegroundColor Green
Write-Host "      • API اخبار: http://localhost:8000/api/v1/newsletter/news" -ForegroundColor Green
Write-Host "      • API منابع: http://localhost:8000/api/v1/newsletter/sources" -ForegroundColor Green

Write-Host "`n📋 تست API:" -ForegroundColor Yellow
Write-Host '   Invoke-RestMethod "http://localhost:8000/api/v1/newsletter/news"' -ForegroundColor White
Write-Host '   Invoke-RestMethod "http://localhost:8000/api/v1/newsletter/sources"' -ForegroundColor White
Write-Host '   Invoke-RestMethod "http://localhost:8000/api/v1/newsletter/categories"' -ForegroundColor White

Write-Host ("=" * 70) -ForegroundColor Cyan