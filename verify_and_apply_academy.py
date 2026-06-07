#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 اسکریپت بررسی و اعمال خودکار تغییرات ماژول آکادمی
این اسکریپت وجود فایل‌ها را بررسی کرده و در صورت عدم وجود، آن‌ها را ایجاد می‌کند.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
API_DIR = ROOT / "api"
WEB = ROOT / "apps" / "web" / "src"

def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"   ✅ ایجاد شد: {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")

def check_and_create_academy_models():
    print("\n📚 بررسی ماژول آکادمی (Models)...")
    path = API_DIR / "modules" / "academy" / "models.py"
    if path.exists():
        print(f"   ℹ️  موجود است: {path.relative_to(ROOT)}")
        return
    
    content = '''# api/modules/academy/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey, Text, Enum as SQLEnum, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from api.core.database import Base
import enum

class CourseLevel(enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class CourseStatus(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class EnrollmentStatus(enum.Enum):
    ENROLLED = "enrolled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CERTIFIED = "certified"

class SDG(Base):
    __tablename__ = "sdgs"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, unique=True, nullable=False)
    title = Column(String(300), nullable=False)
    title_en = Column(String(300))
    description = Column(Text)
    icon = Column(String(100))
    color = Column(String(20))

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    slug = Column(String(200), unique=True, index=True)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    level = Column(SQLEnum(CourseLevel), nullable=False)
    status = Column(SQLEnum(CourseStatus), default=CourseStatus.DRAFT)
    is_free = Column(Boolean, default=True)
    cover_image_url = Column(String(500))
    duration_hours = Column(Float)
    total_sessions = Column(Integer, default=10)
    max_students = Column(Integer, default=100)
    enrolled_count = Column(Integer, default=0)
    rating_average = Column(Float, default=0)
    standards = Column(JSON)  # ["FAO", "IPCC", "SDG-6"]
    language = Column(String(10), default="fa")
    created_at = Column(DateTime, server_default=func.now())
    published_at = Column(DateTime)
    
    sessions = relationship("CourseSession", back_populates="course")
    enrollments = relationship("Enrollment", back_populates="course")

class CourseSession(Base):
    __tablename__ = "course_sessions"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    session_number = Column(Integer, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    video_url = Column(String(500))
    duration_minutes = Column(Integer, default=90)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    
    course = relationship("Course", back_populates="sessions")

class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(SQLEnum(EnrollmentStatus), default=EnrollmentStatus.ENROLLED)
    progress_percent = Column(Float, default=0)
    enrolled_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
    certificate_id = Column(String(100), unique=True)
    
    course = relationship("Course", back_populates="enrollments")

class Discussion(Base):
    __tablename__ = "discussions"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(500))
    content = Column(Text, nullable=False)
    category = Column(String(100), default="discussion")
    reply_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
'''
    write_file(path, content)


def check_and_create_academy_router():
    print("\n🔌 بررسی ماژول آکادمی (Router)...")
    path = API_DIR / "modules" / "academy" / "router.py"
    if path.exists():
        print(f"   ℹ️  موجود است: {path.relative_to(ROOT)}")
        return
    
    content = '''# api/modules/academy/router.py
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.modules.academy.models import Course, CourseStatus, Enrollment, Discussion, SDG

router = APIRouter(prefix="/academy", tags=["Academy"])

class EnrollmentCreate(BaseModel):
    student_id: int

class DiscussionCreate(BaseModel):
    title: Optional[str] = None
    content: str
    category: str = "discussion"
    author_id: int

@router.get("/courses")
async def list_courses(
    category: Optional[str] = None,
    level: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Course).where(Course.status == CourseStatus.PUBLISHED)
    if category:
        query = query.where(Course.category == category)
    result = await db.execute(query)
    courses = result.scalars().all()
    return {
        "count": len(courses),
        "courses": [{
            "id": c.id, "title": c.title, "slug": c.slug, "category": c.category,
            "level": c.level.value, "cover_image_url": c.cover_image_url,
            "duration_hours": c.duration_hours, "enrolled_count": c.enrolled_count,
            "standards": c.standards
        } for c in courses]
    }

@router.get("/courses/{course_id}")
async def get_course(course_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(404, "دوره یافت نشد")
    course.view_count = getattr(course, 'view_count', 0) + 1
    await db.commit()
    return {"id": course.id, "title": course.title, "description": course.description, "standards": course.standards}

@router.post("/courses/{course_id}/enroll")
async def enroll(course_id: int, data: EnrollmentCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(404, "دوره یافت نشد")
    
    new_enrollment = Enrollment(course_id=course_id, student_id=data.student_id)
    db.add(new_enrollment)
    course.enrolled_count += 1
    await db.commit()
    return {"status": "success", "message": "ثبت‌نام با موفقیت انجام شد"}

@router.get("/courses/{course_id}/discussions")
async def list_discussions(course_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Discussion).where(Discussion.course_id == course_id))
    discussions = result.scalars().all()
    return {"discussions": [{"id": d.id, "title": d.title, "content": d.content, "reply_count": d.reply_count} for d in discussions]}

@router.post("/courses/{course_id}/discussions")
async def create_discussion(course_id: int, data: DiscussionCreate, db: AsyncSession = Depends(get_db)):
    new_disc = Discussion(course_id=course_id, author_id=data.author_id, title=data.title, content=data.content, category=data.category)
    db.add(new_disc)
    await db.commit()
    return {"id": new_disc.id, "status": "created"}

@router.get("/statistics")
async def get_stats(db: AsyncSession = Depends(get_db)):
    total_courses = (await db.execute(select(func.count(Course.id)).where(Course.status == CourseStatus.PUBLISHED))).scalar() or 0
    total_enrollments = (await db.execute(select(func.count(Enrollment.id)))).scalar() or 0
    return {"total_courses": total_courses, "total_enrollments": total_enrollments}

@router.get("/categories")
async def list_categories():
    return {
        "categories": [
            {"id": "hydrology", "name": "هیدرولوژی", "icon": "💧", "standards": ["FAO-56", "WMO"]},
            {"id": "soil_carbon", "name": "کربن خاک", "icon": "🌱", "standards": ["IPCC", "Verra"]},
            {"id": "remote_sensing", "name": "سنجش از دور", "icon": "🛰️", "standards": ["NASA", "ESA"]},
            {"id": "sustainable_agriculture", "name": "کشاورزی پایدار", "icon": "🌾", "standards": ["FAO", "SDGs"]},
        ]
    }
'''
    write_file(path, content)


def check_and_create_academy_init():
    print("\n📦 بررسی __init__.py آکادمی...")
    path = API_DIR / "modules" / "academy" / "__init__.py"
    if path.exists():
        print(f"   ℹ️  موجود است: {path.relative_to(ROOT)}")
        return
    write_file(path, "from . import models, router\n")


def check_and_create_academy_frontend():
    print("\n🎨 بررسی صفحه فرانت‌اند آکادمی...")
    path = WEB / "app" / "academy" / "page.tsx"
    if path.exists():
        print(f"   ℹ️  موجود است: {path.relative_to(ROOT)}")
        return
    
    content = '''"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight, Book, Users, Award, Calendar, Clock, Star,
  Play, MessageSquare, CheckCircle, TrendingUp, GraduationCap,
  Globe, Target, Video, FileText, Filter
} from "lucide-react";

const API_BASE = "http://localhost:8000/api/v1/academy";

const SAMPLE_COURSES = [
  {
    id: 1, title: "مبانی هیدرولوژی مهندسی", slug: "hydrology-basics",
    category: "hydrology", level: "beginner",
    description: "آشنایی با مفاهیم پایه هیدرولوژی، چرخه آب، و محاسبات رواناب بر اساس استانداردهای FAO-56 و WMO",
    cover_image_url: "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800",
    duration_hours: 24, enrolled_count: 1250, standards: ["FAO", "WMO", "SDG-6"]
  },
  {
    id: 2, title: "مدیریت کربن خاک و اعتبار کربن", slug: "soil-carbon",
    category: "soil_carbon", level: "intermediate",
    description: "آموزش مدل‌های RothC و IPCC برای اندازه‌گیری و گزارش‌دهی کربن خاک با رویکرد MRV",
    cover_image_url: "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=800",
    duration_hours: 32, enrolled_count: 890, standards: ["IPCC", "Verra", "SDG-13"]
  },
  {
    id: 3, title: "سنجش از دور و پردازش تصاویر ماهواره‌ای", slug: "remote-sensing",
    category: "remote_sensing", level: "advanced",
    description: "کاربرد عملی Sentinel-2 و Landsat در پایش خشکسالی، NDVI و تغییرات کاربری اراضی",
    cover_image_url: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800",
    duration_hours: 40, enrolled_count: 2100, standards: ["NASA", "ESA", "SDG-15"]
  },
  {
    id: 4, title: "کشاورزی پایدار و احیای اراضی خشک", slug: "sustainable-agriculture",
    category: "sustainable_agriculture", level: "beginner",
    description: "تکنیک‌های کشاورزی حفاظتی، آبخیزداری و سازگاری با تغییر اقلیم بر اساس راهنماهای FAO",
    cover_image_url: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800",
    duration_hours: 28, enrolled_count: 3400, standards: ["FAO", "UNDP", "SDG-2"]
  }
];

const CATEGORIES = [
  { id: "all", name: "همه دوره‌ها", icon: "📚" },
  { id: "hydrology", name: "هیدرولوژی", icon: "💧" },
  { id: "soil_carbon", name: "کربن خاک", icon: "🌱" },
  { id: "remote_sensing", name: "سنجش از دور", icon: "🛰️" },
  { id: "sustainable_agriculture", name: "کشاورزی پایدار", icon: "🌾" },
];

const SDGS = [
  { number: 2, title: "گرسنگی صفر", color: "#DDA63A" },
  { number: 6, title: "آب پاک و بهداشت", color: "#26BDE2" },
  { number: 13, title: "اقدام اقلیمی", color: "#3F7E44" },
  { number: 15, title: "حیات در خشکی", color: "#56C02B" },
];

export default function AcademyPage() {
  const [activeCategory, setActiveCategory] = useState("all");
  const [stats, setStats] = useState({ total_courses: 4, total_enrollments: 7640 });

  const filteredCourses = activeCategory === "all" 
    ? SAMPLE_COURSES 
    : SAMPLE_COURSES.filter(c => c.category === activeCategory);

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-600 to-teal-700 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        <div className="relative container mx-auto px-6 py-16">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-6 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-6">
              <div className="p-5 rounded-3xl bg-gradient-to-br from-emerald-500 to-teal-600 shadow-2xl">
                <GraduationCap className="h-12 w-12 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-emerald-400 text-sm font-medium mb-2">آموزش رایگان و تخصصی</p>
                <h1 className="text-5xl md:text-6xl font-black text-white mb-4">آکادمی اکو نوژین</h1>
                <p className="text-xl text-slate-300 max-w-3xl leading-relaxed">
                  دوره‌های تخصصی رایگان در حوزه هیدرولوژی، کربن خاک، سنجش از دور و کشاورزی پایدار 
                  با گواهی‌نامه معتبر و بر اساس استانداردهای FAO، IPCC و اهداف توسعه پایدار (SDGs)
                </p>
              </div
            </div>

            {/* SDGs Badges */}
            <div className="flex flex-wrap gap-3 mt-6">
              {SDGS.map(sdg => (
                <div key={sdg.number} className="flex items-center gap-2 px-4 py-2 rounded-full border border-slate-700 bg-slate-900/50">
                  <div className="w-6 h-6 rounded flex items-center justify-center text-xs font-black text-white" style={{ backgroundColor: sdg.color }}>
                    {sdg.number}
                  </div>
                  <span className="text-sm text-slate-300">{sdg.title}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats */}
      <section className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: "دوره‌های فعال", value: stats.total_courses, icon: Book, color: "#10b981" },
            { label: "دانش‌پذیر", value: stats.total_enrollments.toLocaleString(), icon: Users, color: "#3b82f6" },
            { label: "گواهی‌نامه صادره", value: "۳,۲۰۰+", icon: Award, color: "#f59e0b" },
            { label: "ساعت آموزش", value: "۱۲۰+", icon: Clock, color: "#8b5cf6" },
          ].map((stat, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6"
            >
              <stat.icon className="h-8 w-8 mb-3" style={{ color: stat.color }} />
              <p className="text-3xl font-black text-white mb-1">{stat.value}</p>
              <p className="text-sm text-slate-400">{stat.label}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Categories Filter */}
      <section className="container mx-auto px-6 py-4">
        <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
          {CATEGORIES.map(cat => (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(cat.id)}
              className={`px-5 py-3 rounded-xl font-bold transition-all flex items-center gap-2 whitespace-nowrap ${
                activeCategory === cat.id
                  ? "bg-emerald-600 text-white shadow-lg shadow-emerald-500/30"
                  : "bg-slate-800 text-slate-400 hover:bg-slate-700"
              }`}
            >
              <span>{cat.icon}</span>
              {cat.name}
            </button>
          ))}
        </div>
      </section>

      {/* Courses Grid */}
      <section className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCourses.map((course, idx) => (
            <motion.div
              key={course.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
              className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl overflow-hidden hover:border-emerald-500/50 transition-all group"
            >
              <div className="relative">
                <img src={course.cover_image_url} alt={course.title} className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-500" />
                <div className="absolute top-3 right-3 px-3 py-1 bg-emerald-500/90 text-white text-xs font-bold rounded-full">
                  رایگان
                </div>
                <div className="absolute bottom-3 left-3 flex gap-1">
                  {course.standards.slice(0, 2).map((std, i) => (
                    <span key={i} className="px-2 py-1 bg-slate-900/80 text-slate-200 text-[10px] font-bold rounded">
                      {std}
                    </span>
                  ))}
                </div>
              </div>
              
              <div className="p-6">
                <div className="flex items-center gap-2 mb-3">
                  <span className={`px-2 py-1 rounded text-xs font-bold ${
                    course.level === "beginner" ? "bg-blue-500/20 text-blue-300" :
                    course.level === "intermediate" ? "bg-amber-500/20 text-amber-300" :
                    "bg-red-500/20 text-red-300"
                  }`}>
                    {course.level === "beginner" ? "مبتدی" : course.level === "intermediate" ? "متوسط" : "پیشرفته"}
                  </span>
                  <span className="text-xs text-slate-500 flex items-center gap-1">
                    <Clock className="h-3 w-3" /> {course.duration_hours} ساعت
                  </span>
                </div>
                
                <h3 className="text-xl font-bold text-white mb-2 group-hover:text-emerald-400 transition-colors">
                  {course.title}
                </h3>
                <p className="text-sm text-slate-400 mb-4 line-clamp-2">
                  {course.description}
                </p>
                
                <div className="flex items-center justify-between pt-4 border-t border-slate-800">
                  <div className="flex items-center gap-2 text-xs text-slate-500">
                    <Users className="h-4 w-4" />
                    {course.enrolled_count.toLocaleString()} دانش‌پذیر
                  </div>
                  <button className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-bold flex items-center gap-2 transition-colors">
                    <Play className="h-4 w-4" />
                    شروع دوره
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-6 py-12 border-t border-slate-800">
        <h2 className="text-3xl font-black text-white text-center mb-12">چرا آکادمی اکو نوژین؟</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            {
              icon: Globe,
              title: "استانداردهای بین‌المللی",
              desc: "تمام دوره‌ها بر اساس آخرین راهنماهای FAO، IPCC، WMO و اهداف ۱۷ گانه توسعه پایدار (SDGs) طراحی شده‌اند."
            },
            {
              icon: Video,
              title: "کلاس‌های آنلاین و تالار گفتگو",
              desc: "دسترسی به جلسات زنده، ویدئوهای ضبط‌شده با کیفیت بالا و تالار گفتگوی تخصصی برای پرسش و پاسخ با اساتید."
            },
            {
              icon: Award,
              title: "گواهی‌نامه معتبر",
              desc: "پس از اتمام موفقیت‌آمیز دوره و گذراندن آزمون نهایی، گواهی‌نامه دیجیتال با قابلیت استعلام و QR Code دریافت کنید."
            }
          ].map((feature, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.1 }}
              className="text-center p-6"
            >
              <div className="inline-flex p-4 rounded-2xl bg-emerald-500/10 mb-4">
                <feature.icon className="h-8 w-8 text-emerald-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">{feature.title}</h3>
              <p className="text-slate-400 leading-relaxed">{feature.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
}
'''
    write_file(path, content)


def update_main_py():
    print("\n🔧 بررسی و به‌روزرسانی main.py...")
    path = API_DIR / "main.py"
    if not path.exists():
        print("   ❌ main.py یافت نشد!")
        return
    
    content = path.read_text(encoding="utf-8")
    modified = False
    
    # 1. Check imports
    if "from api.modules.academy.router import router as academy_router" not in content:
        # Find a good place to insert (after other router imports)
        if "from api.modules.library.router" in content:
            content = content.replace(
                "from api.modules.library.router import router as library_router",
                "from api.modules.library.router import router as library_router\nfrom api.modules.academy.router import router as academy_router"
            )
            modified = True
            print("   ✅ import academy_router اضافه شد")
        else:
            # Fallback
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('from api.modules.'):
                    last_import_idx = i
            lines.insert(last_import_idx + 1, "from api.modules.academy.router import router as academy_router")
            content = '\n'.join(lines)
            modified = True
            print("   ✅ import academy_router اضافه شد (روش جایگزین)")

    # 2. Check router registration
    if 'app.include_router(academy_router, prefix="/api/v1")' not in content:
        if 'app.include_router(library_router, prefix="/api/v1")' in content:
            content = content.replace(
                'app.include_router(library_router, prefix="/api/v1")',
                'app.include_router(library_router, prefix="/api/v1")\napp.include_router(academy_router, prefix="/api/v1")'
            )
            modified = True
            print("   ✅ registration academy_router اضافه شد")
        else:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'app.include_router(' in line:
                    last_router_idx = i
            lines.insert(last_router_idx + 1, 'app.include_router(academy_router, prefix="/api/v1")')
            content = '\n'.join(lines)
            modified = True
            print("   ✅ registration academy_router اضافه شد (روش جایگزین)")

    if modified:
        path.write_text(content, encoding="utf-8")
        print("   ✅ main.py با موفقیت به‌روزرسانی شد")
    else:
        print("   ℹ️  main.py از قبل به‌روز است")


def main():
    print("🔍 بررسی و اعمال خودکار تغییرات ماژول آکادمی")
    print("=" * 70)
    
    if not API_DIR.exists() or not WEB.exists():
        print("❌ دایرکتوری‌های اصلی پروژه یافت نشد!")
        return 1
    
    check_and_create_academy_models()
    check_and_create_academy_router()
    check_and_create_academy_init()
    check_and_create_academy_frontend()
    update_main_py()
    
    print("\n" + "=" * 70)
    print("✅ فرآیند بررسی و اعمال تغییرات با موفقیت انجام شد!")
    print("\n🚀 گام‌های بعدی:")
    print("   1. ری‌استارت سرور بک‌اند:")
    print("      uvicorn api.main:app --reload --port 8000")
    print("")
    print("   2. پاک‌سازی کش فرانت‌اند:")
    print("      cd apps\\web")
    print("      Remove-Item .next -Recurse -Force")
    print("")
    print("   3. اجرای فرانت‌اند:")
    print("      pnpm run dev -- -p 3001")
    print("")
    print("   4. مشاهده آکادمی:")
    print("      http://localhost:3001/academy")
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())