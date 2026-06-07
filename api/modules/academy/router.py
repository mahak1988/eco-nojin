"""
Academy Router - آکادمی اکو نوین
دوره‌های تخصصی رایگان با گواهینامه معتبر
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/academy", tags=["Academy"])


# ============ Response Models ============
class CourseResponse(BaseModel):
    id: int
    code: str
    title: str
    category: str
    level: str
    duration_hours: int
    lessons_count: int
    instructor: str
    standards: List[str]
    description: str
    thumbnail: str
    rating: float
    students_count: int
    is_certified: bool


class AcademyStatsResponse(BaseModel):
    total_courses: int
    total_students: int
    total_certificates: int
    total_hours: int
    categories: List[str]
    active_courses: int


# ============ Mock Database ============
COURSES_DB = [
    {
        "id": 1,
        "code": "HYD-101",
        "title": "مبانی هیدرولوژی کاربردی",
        "title_en": "Applied Hydrology Fundamentals",
        "category": "hydrology",
        "level": "beginner",
        "duration_hours": 40,
        "lessons_count": 12,
        "instructor": "دکتر محمد رضایی",
        "standards": ["FAO", "WMO"],
        "description": "آشنایی با چرخه هیدرولوژیکی،平衡 آبی، و مدیریت منابع آب بر اساس استانداردهای FAO",
        "description_en": "Introduction to hydrological cycle, water balance, and water resource management based on FAO standards",
        "objectives": [
            "درک چرخه هیدرولوژیکی",
            "محاسبه balance آبی",
            "مدیریت منابع آب پایدار",
            "کاربرد مدل‌های هیدرولوژیکی"
        ],
        "prerequisites": ["آشنایی با ریاضیات پایه"],
        "thumbnail": "/images/courses/hydrology-101.jpg",
        "rating": 4.8,
        "students_count": 1250,
        "is_certified": True,
        "created_at": "2024-01-15T10:00:00Z"
    },
    {
        "id": 2,
        "code": "CRB-201",
        "title": "محاسبه کربن و اعتبار کربن",
        "title_en": "Carbon Accounting & Credits",
        "category": "carbon",
        "level": "intermediate",
        "duration_hours": 60,
        "lessons_count": 18,
        "instructor": "دکتر سارا احمدی",
        "standards": ["IPCC", "ISO 14064"],
        "description": "محاسبه ردپای کربن، پروژه‌های offset کربن، و بازار اعتبار کربن بر اساس پروتکل IPCC",
        "description_en": "Carbon footprint calculation, carbon offset projects, and carbon credit market based on IPCC protocol",
        "objectives": [
            "محاسبه ردپای کربن",
            "طراحی پروژه‌های offset",
            "درک بازار کربن",
            "گزارش‌دهی IPCC"
        ],
        "prerequisites": ["HYD-101", "آشنایی با محیط زیست"],
        "thumbnail": "/images/courses/carbon-201.jpg",
        "rating": 4.9,
        "students_count": 890,
        "is_certified": True,
        "created_at": "2024-02-20T14:30:00Z"
    },
    {
        "id": 3,
        "code": "SOL-102",
        "title": "علم خاک و مدیریت پایدار",
        "title_en": "Soil Science & Sustainable Management",
        "category": "soil",
        "level": "beginner",
        "duration_hours": 35,
        "lessons_count": 10,
        "instructor": "دکتر علی کریمی",
        "standards": ["FAO", "GSP"],
        "description": "خواص فیزیکی و شیمیایی خاک، طبقه‌بندی خاک، و مدیریت پایدار بر اساس FAO",
        "description_en": "Physical and chemical soil properties, soil classification, and sustainable management based on FAO",
        "objectives": [
            "شناخت انواع خاک",
            "تحلیل خواص خاک",
            "مدیریت حاصلخیزی",
            "جلوگیری از فرسایش"
        ],
        "prerequisites": [],
        "thumbnail": "/images/courses/soil-102.jpg",
        "rating": 4.7,
        "students_count": 1580,
        "is_certified": True,
        "created_at": "2024-03-10T09:15:00Z"
    },
    {
        "id": 4,
        "code": "RS-301",
        "title": "سنجش از دور پیشرفته",
        "title_en": "Advanced Remote Sensing",
        "category": "remote_sensing",
        "level": "advanced",
        "duration_hours": 80,
        "lessons_count": 24,
        "instructor": "دکتر مریم حسینی",
        "standards": ["ESA", "NASA"],
        "description": "پردازش تصاویر ماهواره‌ای، تحلیل طیفی، و کاربرد در پایش محیط زیست با Sentinel و Landsat",
        "description_en": "Satellite image processing, spectral analysis, and environmental monitoring applications with Sentinel and Landsat",
        "objectives": [
            "پردازش تصاویر ماهواره‌ای",
            "محاسبه شاخص‌های طیفی",
            "طبقه‌بندی پوشش زمین",
            "پایش تغییرات"
        ],
        "prerequisites": ["HYD-101", "آشنایی با GIS"],
        "thumbnail": "/images/courses/rs-301.jpg",
        "rating": 4.9,
        "students_count": 720,
        "is_certified": True,
        "created_at": "2024-04-05T11:45:00Z"
    },
    {
        "id": 5,
        "code": "AGRI-202",
        "title": "کشاورزی پایدار و امنیت غذایی",
        "title_en": "Sustainable Agriculture & Food Security",
        "category": "sustainable_agriculture",
        "level": "intermediate",
        "duration_hours": 50,
        "lessons_count": 15,
        "instructor": "دکتر رضا نوروزی",
        "standards": ["FAO", "SDGs"],
        "description": "اصول کشاورزی پایدار، مدیریت آب کشاورزی، و امنیت غذایی بر اساس اهداف توسعه پایدار SDG 2",
        "description_en": "Sustainable agriculture principles, agricultural water management, and food security based on SDG 2",
        "objectives": [
            "اصول کشاورزی پایدار",
            "مدیریت آب کشاورزی",
            "افزایش بهره‌وری",
            "امنیت غذایی"
        ],
        "prerequisites": ["SOL-102"],
        "thumbnail": "/images/courses/agri-202.jpg",
        "rating": 4.8,
        "students_count": 1120,
        "is_certified": True,
        "created_at": "2024-05-12T16:20:00Z"
    },
    {
        "id": 6,
        "code": "DRY-302",
        "title": "مدیریت خشکسالی و تغییر اقلیم",
        "title_en": "Drought Management & Climate Change",
        "category": "hydrology",
        "level": "advanced",
        "duration_hours": 70,
        "lessons_count": 20,
        "instructor": "دکتر فاطمه محمدی",
        "standards": ["IPCC", "WMO", "UNCCD"],
        "description": "پایش خشکسالی، شاخص‌های اقلیمی، و استراتژی‌های سازگاری بر اساس گزارش‌های IPCC",
        "description_en": "Drought monitoring, climate indices, and adaptation strategies based on IPCC reports",
        "objectives": [
            "پایش خشکسالی",
            "تحلیل شاخص‌های اقلیمی",
            "استراتژی‌های سازگاری",
            "مدیریت ریسک"
        ],
        "prerequisites": ["HYD-101", "CRB-201"],
        "thumbnail": "/images/courses/dry-302.jpg",
        "rating": 4.9,
        "students_count": 650,
        "is_certified": True,
        "created_at": "2024-06-01T13:00:00Z"
    }
]


# ============ Endpoints ============
@router.get("/statistics", response_model=AcademyStatsResponse)
async def get_academy_stats():
    """آمار آکادمی"""
    total_hours = sum(c["duration_hours"] for c in COURSES_DB)
    categories = list(set(c["category"] for c in COURSES_DB))
    
    return AcademyStatsResponse(
        total_courses=len(COURSES_DB),
        total_students=sum(c["students_count"] for c in COURSES_DB),
        total_certificates=sum(c["students_count"] for c in COURSES_DB) // 2,
        total_hours=total_hours,
        categories=categories,
        active_courses=len([c for c in COURSES_DB if c["students_count"] > 0])
    )


@router.get("/courses", response_model=List[CourseResponse])
async def get_courses(
    category: Optional[str] = None,
    level: Optional[str] = None,
    standard: Optional[str] = None
):
    """لیست دوره‌ها با فیلتر"""
    courses = COURSES_DB
    
    if category:
        courses = [c for c in courses if c["category"] == category]
    if level:
        courses = [c for c in courses if c["level"] == level]
    if standard:
        courses = [c for c in courses if standard in c["standards"]]
    
    return courses


@router.get("/courses/{course_id}", response_model=CourseResponse)
async def get_course(course_id: int):
    """جزئیات یک دوره"""
    course = next((c for c in COURSES_DB if c["id"] == course_id), None)
    if not course:
        raise HTTPException(status_code=404, detail="دوره یافت نشد")
    return course


@router.get("/categories")
async def get_categories():
    """لیست دسته‌بندی‌ها"""
    return {
        "categories": [
            {"id": "hydrology", "name": "هیدرولوژی", "icon": "Droplet", "count": 2},
            {"id": "carbon", "name": "کربن و اقلیم", "icon": "Leaf", "count": 1},
            {"id": "soil", "name": "علم خاک", "icon": "Mountain", "count": 1},
            {"id": "remote_sensing", "name": "سنجش از دور", "icon": "Satellite", "count": 1},
            {"id": "sustainable_agriculture", "name": "کشاورزی پایدار", "icon": "Sprout", "count": 1}
        ]
    }


@router.get("/standards")
async def get_standards():
    """لیست استانداردها"""
    return {
        "standards": [
            {"code": "FAO", "name": "سازمان خواربار و کشاورزی ملل متحد", "url": "https://www.fao.org"},
            {"code": "IPCC", "name": "هیئت بین‌دولتی تغییر اقلیم", "url": "https://www.ipcc.ch"},
            {"code": "SDGs", "name": "اهداف توسعه پایدار", "url": "https://sdgs.un.org"},
            {"code": "WMO", "name": "سازمان جهانی هواشناسی", "url": "https://public.wmo.int"},
            {"code": "ISO 14064", "name": "استاندارد گازهای گلخانه‌ای", "url": "https://www.iso.org"},
            {"code": "UNCCD", "name": "کنوانسیون مبارزه با بیابان‌زایی", "url": "https://www.unccd.int"}
        ]
    }
