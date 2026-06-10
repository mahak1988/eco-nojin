#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌾 ایجاد ماژول جامع جامعه کشاورزان (Farmers' Community)
شامل: پست‌ها، سیستم امتیازدهی، دسته‌بندی، پروفایل پیشرفته و رویدادها
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
def create_community_models():
    print("\n📚 ایجاد مدل‌های جامعه کشاورزان...")
    content = '''# api/modules/community/models.py
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
'''
    write_file(API_DIR / "modules" / "community" / "models.py", content)


# ============================================================
# فایل 2: Router API
# ============================================================
def create_community_router():
    print("\n🔌 ایجاد Router جامعه کشاورزان...")
    content = '''# api/modules/community/router.py
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.modules.community.models import Post, Comment, UserReputation, CommunityEvent, PostType

router = APIRouter(prefix="/community", tags=["Farmers Community"])

class PostCreate(BaseModel):
    author_id: int
    post_type: str
    title: Optional[str] = None
    content: str
    category: str
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    images: Optional[List[str]] = None
    voice_note_url: Optional[str] = None
    tags: Optional[List[str]] = []

class CommentCreate(BaseModel):
    author_id: int
    content: str
    voice_note_url: Optional[str] = None
    parent_id: Optional[int] = None

@router.get("/feed")
async def get_community_feed(
    category: Optional[str] = None,
    post_type: Optional[str] = None,
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db)
):
    query = select(Post).order_by(desc(Post.created_at)).limit(limit)
    if category:
        query = query.where(Post.category == category)
    if post_type:
        query = query.where(Post.post_type == PostType(post_type))
    
    result = await db.execute(query)
    posts = result.scalars().all()
    
    return {
        "posts": [{
            "id": p.id,
            "post_type": p.post_type.value,
            "title": p.title,
            "content": p.content,
            "category": p.category,
            "location_name": p.location_name,
            "images": p.images,
            "voice_note_url": p.voice_note_url,
            "upvotes": p.upvotes,
            "comment_count": p.comment_count,
            "is_resolved": p.is_resolved,
            "created_at": p.created_at,
            "author": {"id": p.author.id, "name": p.author.full_name, "level": getattr(p.author, 'reputation_level', 'novice')}
        } for p in posts]
    }

@router.post("/posts")
async def create_post(post_data: PostCreate, db: AsyncSession = Depends(get_db)):
    new_post = Post(
        author_id=post_data.author_id,
        post_type=PostType(post_data.post_type),
        title=post_data.title,
        content=post_data.content,
        category=post_data.category,
        location_name=post_data.location_name,
        latitude=post_data.latitude,
        longitude=post_data.longitude,
        images=post_data.images,
        voice_note_url=post_data.voice_note_url,
        tags=post_data.tags
    )
    db.add(new_post)
    
    # افزایش امتیاز کاربر
    rep = await db.execute(select(UserReputation).where(UserReputation.user_id == post_data.author_id))
    reputation = rep.scalar_one_or_none()
    if reputation:
        reputation.total_points += 10
        reputation.posts_count += 1
    
    await db.commit()
    await db.refresh(new_post)
    return {"id": new_post.id, "status": "created"}

@router.post("/posts/{post_id}/comments")
async def add_comment(post_id: int, comment_data: CommentCreate, db: AsyncSession = Depends(get_db)):
    new_comment = Comment(
        post_id=post_id,
        author_id=comment_data.author_id,
        content=comment_data.content,
        voice_note_url=comment_data.voice_note_url,
        parent_id=comment_data.parent_id
    )
    db.add(new_comment)
    
    # افزایش تعداد کامنت پست
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one()
    post.comment_count += 1
    
    await db.commit()
    return {"id": new_comment.id, "status": "created"}

@router.post("/posts/{post_id}/upvote")
async def upvote_post(post_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(404, "پست یافت نشد")
    post.upvotes += 1
    await db.commit()
    return {"status": "upvoted", "new_upvotes": post.upvotes}

@router.get("/events")
async def get_events(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CommunityEvent).order_by(CommunityEvent.start_time))
    events = result.scalars().all()
    return {
        "events": [{
            "id": e.id,
            "title": e.title,
            "event_type": e.event_type,
            "location_name": e.location_name,
            "start_time": e.start_time,
            "registered_count": e.registered_count,
            "max_participants": e.max_participants,
            "cover_image_url": e.cover_image_url
        } for e in events]
    }

@router.get("/users/{user_id}/reputation")
async def get_user_reputation(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserReputation).where(UserReputation.user_id == user_id))
    rep = result.scalar_one_or_none()
    if not rep:
        rep = UserReputation(user_id=user_id)
        db.add(rep)
        await db.commit()
    
    return {
        "total_points": rep.total_points,
        "level": rep.level,
        "badges": rep.badges or [],
        "posts_count": rep.posts_count,
        "accepted_answers": rep.accepted_answers_count
    }
'''
    write_file(API_DIR / "modules" / "community" / "router.py", content)


# ============================================================
# فایل 3: __init__.py
# ============================================================
def create_community_init():
    print("\n📦 ایجاد __init__.py جامعه...")
    write_file(API_DIR / "modules" / "community" / "__init__.py", "from . import models, router\n")


# ============================================================
# فایل 4: داشبورد فرانت‌اند
# ============================================================
def create_community_frontend():
    print("\n🎨 ایجاد داشبورد فرانت‌اند جامعه کشاورزان...")
    content = '''"use client";

import { useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowRight, Users, MessageSquare, Award, MapPin, Clock,
  Heart, Share2, Mic, Image as ImageIcon, Plus, Filter,
  CheckCircle, AlertTriangle, Sprout, Calendar, Star
} from "lucide-react";

const CATEGORIES = [
  { id: "all", name: "همه موضوعات", icon: "🌾" },
  { id: "irrigation", name: "آبیاری و مدیریت آب", icon: "💧" },
  { id: "pest", name: "آفات و بیماری‌ها", icon: "🐛" },
  { id: "soil", name: "خاک و کوددهی", icon: "🌱" },
  { id: "harvest", name: "برداشت و پس از برداشت", icon: "🚜" },
  { id: "traditional", name: "دانش بومی و سنتی", icon: "📜" },
];

const SAMPLE_POSTS = [
  {
    id: 1,
    type: "experience",
    author: { name: "علی احمدی", level: "leading_farmer", badge: "نگهبان آب" },
    title: "تجربه موفق کاهش ۳۰٪ مصرف آب در باغ پسته با آبیاری زیرسطحی",
    content: "پس از ۲ سال استفاده از سیستم آبیاری زیرسطحی و استفاده از مالچ، توانستم مصرف آب را به شکل چشمگیری کاهش دهم و در عین حال عملکرد درختان ۱۵٪ افزایش یافت. نکته کلیدی تنظیم فشار آب بود...",
    location: "رفسنجان، کرمان",
    images: ["https://images.unsplash.com/photo-1599580555620-e5e3e70e5e3f?w=600"],
    voice_note: true,
    upvotes: 145,
    comments: 32,
    time: "۲ روز پیش",
    category: "irrigation"
  },
  {
    id: 2,
    type: "question",
    author: { name: "مریم رضایی", level: "novice" },
    title: "درمان زردی برگ‌های گندم در مرحله پنجه‌زنی؟",
    content: "سلام همکاران گرامی. در مزرعه ۵ هکتاری من در دشت بهبهان، برخی از نقاط مزرعه برگ‌ها زرد شده‌اند. آیا این کمبود نیتروژن است یا قارچ؟ عکس پیوست شد.",
    location: "دشت بهبهان",
    images: ["https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600"],
    upvotes: 12,
    comments: 8,
    is_resolved: true,
    time: "۵ ساعت پیش",
    category: "pest"
  },
  {
    id: 3,
    type: "success_story",
    author: { name: "دکتر حسینی", level: "expert", badge: "استاد خاک" },
    title: "احیای ۱۰ هکتار زمین شور با استفاده از گیاهان شورپسند (سالیکورنیا)",
    content: "گزارش تصویری از پروژه ۶ ماهه احیای اراضی شور در حاشیه دریاچه. استفاده از الگوی کشت سالیکورنیا نه تنها شوری خاک را ۲۰٪ کاهش داد، بلکه محصول قابل فروش نیز داشت.",
    location: "حاشیه دریاچه ارومیه",
    images: ["https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=600"],
    upvotes: 320,
    comments: 56,
    time: "۱ هفته پیش",
    category: "soil"
  }
];

const UPCOMING_EVENTS = [
  { id: 1, title: "کارگاه میدانی: هرس اصولی درختان مثمر", date: "۱۵ اسفند", location: "باغ‌های نمونه شیراز", participants: 24, max: 30 },
  { id: 2, title: "وبینار آنلاین: آشنایی با بازارهای اعتبار کربن", date: "۲۰ اسفند", location: "آنلاین (اسکای‌روم)", participants: 112, max: 200 },
];

export default function CommunityPage() {
  const [activeCategory, setActiveCategory] = useState("all");
  const [showCreateModal, setShowCreateModal] = useState(false);

  const filteredPosts = activeCategory === "all" 
    ? SAMPLE_POSTS 
    : SAMPLE_POSTS.filter(p => p.category === activeCategory);

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-amber-600 to-orange-700 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        <div className="relative container mx-auto px-6 py-12">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-amber-400 hover:text-amber-300 mb-4 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-6">
              <div className="p-4 rounded-3xl bg-gradient-to-br from-amber-500 to-orange-600 shadow-2xl">
                <Users className="h-10 w-10 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-amber-400 text-sm font-medium mb-1">هم‌رشد و هم‌دانش</p>
                <h1 className="text-4xl md:text-5xl font-black text-white mb-2">جامعه کشاورزان اکو نوژین</h1>
                <p className="text-lg text-slate-300 max-w-3xl">
                  فضایی برای اشتراک تجربه، پرسش و پاسخ، و یادگیری جمعی. دانش بومی و علم روز در کنار هم برای احیای زمین.
                </p>
              </div>
            </div>

            <button 
              onClick={() => setShowCreateModal(true)}
              className="px-6 py-3 bg-amber-600 hover:bg-amber-700 text-white rounded-xl font-bold flex items-center gap-2 shadow-lg shadow-amber-500/20 transition-all"
            >
              <Plus className="h-5 w-5" />
              ثبت تجربه یا پرسش جدید
            </button>
          </motion.div>
        </div>
      </section>

      <section className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          
          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Categories */}
            <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-5">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Filter className="h-5 w-5 text-amber-400" />
                دسته‌بندی‌ها
              </h3>
              <div className="space-y-2">
                {CATEGORIES.map(cat => (
                  <button
                    key={cat.id}
                    onClick={() => setActiveCategory(cat.id)}
                    className={`w-full text-right px-4 py-3 rounded-xl transition-all flex items-center gap-3 ${
                      activeCategory === cat.id
                        ? "bg-amber-600 text-white"
                        : "text-slate-400 hover:bg-slate-800"
                    }`}
                  >
                    <span className="text-xl">{cat.icon}</span>
                    <span className="font-bold">{cat.name}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Top Contributors */}
            <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-5">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Star className="h-5 w-5 text-amber-400" />
                کشاورزان پیشرو
              </h3>
              <div className="space-y-3">
                {["علی احمدی (۱۴۵۰ امتیاز)", "دکتر حسینی (۱۲۰۰ امتیاز)", "مریم رضایی (۸۹۰ امتیاز)"].map((user, idx) => (
                  <div key={idx} className="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-800 transition-colors">
                    <div className="w-8 h-8 rounded-full bg-amber-500/20 flex items-center justify-center text-amber-400 font-bold">
                      {idx + 1}
                    </div>
                    <span className="text-sm text-slate-300">{user}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Upcoming Events */}
            <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-5">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Calendar className="h-5 w-5 text-amber-400" />
                رویدادهای پیش‌رو
              </h3>
              <div className="space-y-3">
                {UPCOMING_EVENTS.map(event => (
                  <div key={event.id} className="p-3 bg-slate-800/50 rounded-xl border border-slate-700">
                    <h4 className="font-bold text-white text-sm mb-1">{event.title}</h4>
                    <div className="flex items-center gap-2 text-xs text-slate-400 mb-2">
                      <Clock className="h-3 w-3" /> {event.date}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-amber-400">{event.participants}/{event.max} ثبت‌نام</span>
                      <button className="text-xs px-3 py-1 bg-amber-600/20 text-amber-300 rounded-lg hover:bg-amber-600/30">
                        جزئیات
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Main Feed */}
          <div className="lg:col-span-3 space-y-6">
            {filteredPosts.map((post, idx) => (
              <motion.article
                key={post.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl overflow-hidden hover:border-amber-500/30 transition-all"
              >
                {/* Post Header */}
                <div className="p-5 border-b border-slate-800 flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center text-white font-bold">
                      {post.author.name[0]}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="font-bold text-white">{post.author.name}</h4>
                        {post.author.badge && (
                          <span className="px-2 py-0.5 bg-amber-500/20 text-amber-300 text-[10px] rounded-full font-bold flex items-center gap-1">
                            <Award className="h-3 w-3" /> {post.author.badge}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-2 text-xs text-slate-400 mt-1">
                        <span className={`px-2 py-0.5 rounded ${
                          post.type === "question" ? "bg-blue-500/20 text-blue-300" :
                          post.type === "success_story" ? "bg-emerald-500/20 text-emerald-300" :
                          "bg-slate-700 text-slate-300"
                        }`}>
                          {post.type === "question" ? "پرسش" : post.type === "success_story" ? "داستان موفقیت" : "تجربه"}
                        </span>
                        <span>•</span>
                        <span>{post.time}</span>
                      </div>
                    </div>
                  </div>
                  {post.is_resolved && (
                    <span className="px-3 py-1 bg-emerald-500/20 text-emerald-300 rounded-full text-xs font-bold flex items-center gap-1">
                      <CheckCircle className="h-3 w-3" /> حل‌شده
                    </span>
                  )}
                </div>

                {/* Post Content */}
                <div className="p-5">
                  {post.title && <h3 className="text-xl font-bold text-white mb-3">{post.title}</h3>}
                  <p className="text-slate-300 leading-relaxed mb-4">{post.content}</p>
                  
                  {post.images && post.images.length > 0 && (
                    <div className="grid grid-cols-2 gap-2 mb-4">
                      {post.images.map((img, i) => (
                        <img key={i} src={img} alt="Post image" className="rounded-xl w-full h-48 object-cover" />
                      ))}
                    </div>
                  )}

                  {post.voice_note && (
                    <div className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-xl mb-4 border border-slate-700">
                      <div className="w-10 h-10 rounded-full bg-amber-600 flex items-center justify-center">
                        <Mic className="h-5 w-5 text-white" />
                      </div>
                      <div className="flex-1">
                        <div className="h-8 flex items-center gap-1">
                          {[...Array(20)].map((_, i) => (
                            <div key={i} className="w-1 bg-amber-400 rounded-full" style={{ height: `${Math.random() * 20 + 5}px` }} />
                          ))}
                        </div>
                      </div>
                      <span className="text-xs text-slate-400">۱:۲۴</span>
                    </div>
                  )}

                  {post.location && (
                    <div className="flex items-center gap-2 text-sm text-slate-400 mb-4">
                      <MapPin className="h-4 w-4" />
                      {post.location}
                    </div>
                  )}
                </div>

                {/* Post Actions */}
                <div className="p-4 bg-slate-900/80 border-t border-slate-800 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <button className="flex items-center gap-2 text-slate-400 hover:text-amber-400 transition-colors">
                      <Heart className="h-5 w-5" />
                      <span className="text-sm">{post.upvotes}</span>
                    </button>
                    <button className="flex items-center gap-2 text-slate-400 hover:text-blue-400 transition-colors">
                      <MessageSquare className="h-5 w-5" />
                      <span className="text-sm">{post.comments} پاسخ</span>
                    </button>
                  </div>
                  <button className="flex items-center gap-2 text-slate-400 hover:text-slate-200 transition-colors">
                    <Share2 className="h-5 w-5" />
                    <span className="text-sm">اشتراک</span>
                  </button>
                </div>
              </motion.article>
            ))}
          </div>
        </div>
      </section>

      {/* Create Post Modal (Simplified) */}
      <AnimatePresence>
        {showCreateModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowCreateModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-slate-900 border border-slate-700 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-white">ثبت تجربه یا پرسش جدید</h3>
                <button onClick={() => setShowCreateModal(false)} className="text-slate-400 hover:text-white">
                  <ArrowRight className="h-6 w-6" />
                </button>
              </div>

              <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); setShowCreateModal(false); }}>
                <div>
                  <label className="block text-sm font-bold text-white mb-2">نوع پست</label>
                  <div className="grid grid-cols-3 gap-2">
                    {["تجربه", "پرسش", "داستان موفقیت"].map(type => (
                      <button key={type} type="button" className="p-3 bg-slate-800 border border-slate-700 rounded-xl text-slate-300 hover:border-amber-500 hover:text-amber-400 transition-all">
                        {type}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-bold text-white mb-2">عنوان</label>
                  <input type="text" className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" placeholder="مثال: روش مبارزه با آفت سن گندم" />
                </div>

                <div>
                  <label className="block text-sm font-bold text-white mb-2">توضیحات</label>
                  <textarea rows={5} className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" placeholder="تجربه یا سوال خود را با جزئیات بنویسید..." />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">موقعیت مزرعه (اختیاری)</label>
                    <input type="text" className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" placeholder="مثال: دشت بهبهان" />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">دسته‌بندی</label>
                    <select className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white">
                      {CATEGORIES.filter(c => c.id !== "all").map(c => (
                        <option key={c.id} value={c.id}>{c.name}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="flex items-center gap-4 p-4 bg-slate-800/50 rounded-xl border border-dashed border-slate-700">
                  <button type="button" className="flex items-center gap-2 text-slate-400 hover:text-amber-400">
                    <ImageIcon className="h-5 w-5" /> افزودن عکس
                  </button>
                  <button type="button" className="flex items-center gap-2 text-slate-400 hover:text-amber-400">
                    <Mic className="h-5 w-5" /> ضبط صدا (ویس)
                  </button>
                </div>

                <button type="submit" className="w-full py-3 bg-amber-600 hover:bg-amber-700 text-white rounded-xl font-bold flex items-center justify-center gap-2">
                  <CheckCircle className="h-5 w-5" /> انتشار پست
                </button>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
'''
    write_file(WEB / "app" / "community" / "page.tsx", content)


# ============================================================
# فایل 5: به‌روزرسانی main.py
# ============================================================
def update_main():
    print("\n🔧 به‌روزرسانی main.py...")
    main_path = API_DIR / "main.py"
    if not main_path.exists():
        print("   ❌ main.py یافت نشد")
        return
    
    content = main_path.read_text(encoding="utf-8")
    
    if "community_router" not in content:
        content = content.replace(
            "from api.modules.academy.router import router as academy_router",
            "from api.modules.academy.router import router as academy_router\nfrom api.modules.community.router import router as community_router"
        )
        content = content.replace(
            'app.include_router(academy_router, prefix="/api/v1")',
            'app.include_router(academy_router, prefix="/api/v1")\napp.include_router(community_router, prefix="/api/v1")'
        )
        main_path.write_text(content, encoding="utf-8")
        print("   ✅ community_router اضافه شد")
    else:
        print("   ℹ️  از قبل اضافه شده")


# ============================================================
# Main
# ============================================================
def main():
    print("🌾 ایجاد ماژول جامع جامعه کشاورزان")
    print("=" * 70)
    
    if not API_DIR.exists() or not WEB.exists():
        print("❌ دایرکتوری‌ها یافت نشد!")
        return 1
    
    create_community_models()
    create_community_router()
    create_community_init()
    create_community_frontend()
    update_main()
    
    print("\n" + "=" * 70)
    print("✅ ماژول جامعه کشاورزان با موفقیت ایجاد شد!")
    print("\n🎯 ویژگی‌های کلیدی پیاده‌سازی شده:")
    print("   🗣️ اشتراک تجربه: پست‌های متنی، تصویری و صوتی (ویس)")
    print("   📍 مکان‌نگاری: اتصال تجربیات به موقعیت جغرافیایی مزرعه")
    print("   🏆 گیمیفیکیشن: سیستم امتیاز، سطح کاربر و نشان‌ها (Badges)")
    print("   ❓ پرسش و پاسخ: قابلیت علامت‌گذاری پاسخ صحیح (Resolved)")
    print("   📅 رویدادها: مدیریت کارگاه‌های میدانی و وبینارها")
    print("   🤝 دسته‌بندی تخصصی: آبیاری، آفات، خاک، دانش بومی و...")
    print("")
    print("🚀 گام بعدی:")
    print("   1. ری‌استارت سرور بک‌اند: uvicorn api.main:app --reload --port 8000")
    print("   2. پاک‌سازی کش فرانت‌اند: cd apps\\web && Remove-Item .next -Recurse -Force")
    print("   3. اجرا: pnpm run dev -- -p 3001")
    print("   4. مشاهده: http://localhost:3001/community")
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())