"""
Database Models for Education Module
مدل‌های پایگاه داده برای ماژول آموزش‌یار

این ماژول شامل مدل‌های SQLAlchemy برای:
- دوره‌های آموزشی (Courses)
- درس‌ها و سرفصل‌ها (Lessons/Curriculum)
- محتوای آموزشی (Educational Content)
- ثبت‌نام کاربران (Enrollments)
- پیشرفت یادگیری (Learning Progress)
- آزمون‌ها و ارزیابی‌ها (Quizzes/Assessments)
- گواهینامه‌ها (Certificates)
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey,
    Text, Boolean, JSON, Enum as SQLEnum, Table, Index, Time
)
from sqlalchemy.orm import relationship, declarative_base, Mapped, mapped_column
from sqlalchemy.sql import func

Base = declarative_base()


class CourseLevel(str, Enum):
    """سطح دشواری دوره"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class CourseStatus(str, Enum):
    """وضعیت انتشار دوره"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    UNPUBLISHED = "unpublished"


class ContentType(str, Enum):
    """انواع محتوای آموزشی"""
    VIDEO = "video"
    TEXT = "text"
    PDF = "pdf"
    PRESENTATION = "presentation"
    INTERACTIVE = "interactive"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"
    EXTERNAL_LINK = "external_link"
    SCORM = "scorm"


class EnrollmentStatus(str, Enum):
    """وضعیت ثبت‌نام"""
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"
    EXPIRED = "expired"
    PENDING = "pending"


class CertificateStatus(str, Enum):
    """وضعیت گواهینامه"""
    PENDING = "pending"
    ISSUED = "issued"
    REVOKED = "revoked"
    EXPIRED = "expired"


# ============================================================================
# Course Models
# ============================================================================

class Course(Base):
    """
    دوره آموزشی
    هسته اصلی سیستم آموزش‌یار
    """
    __tablename__ = "education_courses"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # اطلاعات پایه
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    title_fa: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    
    # توضیحات
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_fa: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # سطح و دسته‌بندی
    level: Mapped[str] = mapped_column(SQLEnum(CourseLevel), default=CourseLevel.BEGINNER)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # وضعیت
    status: Mapped[str] = mapped_column(SQLEnum(CourseStatus), default=CourseStatus.DRAFT)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_free: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # قیمت
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="IRR")
    discount_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # مدت زمان
    duration_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    estimated_weeks: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # زبان
    language: Mapped[str] = mapped_column(String(10), default="fa")
    subtitles: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # پیش‌نیازها
    prerequisites: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    target_audience: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    learning_objectives: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # تصویر و رسانه
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    promo_video_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # آمار
    enrolled_count: Mapped[int] = mapped_column(Integer, default=0)
    completed_count: Mapped[int] = mapped_column(Integer, default=0)
    rating_average: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rating_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # مدرس/مدرسین
    instructor_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    co_instructors: Mapped[Optional[List[int]]] = mapped_column(JSON, nullable=True)
    
    # سازمان/موسسه
    organization_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # روابط
    lessons: Mapped[List["Lesson"]] = relationship(
        "Lesson", back_populates="course", cascade="all, delete-orphan", order_by="Lesson.order"
    )
    enrollments: Mapped[List["Enrollment"]] = relationship(
        "Enrollment", back_populates="course", cascade="all, delete-orphan"
    )
    certificates: Mapped[List["Certificate"]] = relationship(
        "Certificate", back_populates="course", cascade="all, delete-orphan"
    )
    quizzes: Mapped[List["Quiz"]] = relationship(
        "Quiz", back_populates="course", cascade="all, delete-orphan"
    )
    
    # ایندکس‌ها
    __table_args__ = (
        Index('idx_course_category_status', 'category', 'status'),
        Index('idx_course_level', 'level'),
        {'sqlite_autoincrement': True}
    )
    
    def __repr__(self):
        return f"<Course(id={self.id}, title='{self.title}', level='{self.level}')>"


class Lesson(Base):
    """
    درس‌ها و سرفصل‌های دوره
    """
    __tablename__ = "education_lessons"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("education_courses.id"), nullable=False)
    
    # اطلاعات درس
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    title_fa: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # ترتیب و ساختار
    order: Mapped[int] = mapped_column(Integer, default=0)
    section: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # بخش/فصل
    section_order: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # نوع و محتوا
    lesson_type: Mapped[str] = mapped_column(
        SQLEnum("lecture", "reading", "quiz", "assignment", "discussion", name="lesson_type"),
        default="lecture"
    )
    
    # مدت زمان
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # وضعیت
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    is_preview: Mapped[bool] = mapped_column(Boolean, default=False)  # قابل مشاهده رایگان
    
    # قفل‌گذاری
    unlock_after_lesson_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("education_lessons.id"), nullable=True
    )
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # روابط
    course: Mapped["Course"] = relationship("Course", back_populates="lessons")
    content_items: Mapped[List["ContentItem"]] = relationship(
        "ContentItem", back_populates="lesson", cascade="all, delete-orphan"
    )
    progress_records: Mapped[List["LearningProgress"]] = relationship(
        "LearningProgress", back_populates="lesson", cascade="all, delete-orphan"
    )
    
    # ایندکس‌ها
    __table_args__ = (
        Index('idx_lesson_course_order', 'course_id', 'order'),
        {'sqlite_autoincrement': True}
    )
    
    def __repr__(self):
        return f"<Lesson(id={self.id}, course_id={self.course_id}, title='{self.title}')>"


class ContentItem(Base):
    """
    آیتم‌های محتوای آموزشی
    هر درس می‌تواند چندین آیتم محتوا داشته باشد
    """
    __tablename__ = "education_content_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lesson_id: Mapped[int] = mapped_column(Integer, ForeignKey("education_lessons.id"), nullable=False)
    
    # اطلاعات محتوا
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(SQLEnum(ContentType), nullable=False)
    
    # URL یا مسیر فایل
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # متادیتا
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # ترتیب نمایش
    order: Mapped[int] = mapped_column(Integer, default=0)
    
    # متن جایگزین/توضیحات
    alt_text: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # تنظیمات
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
    allow_download: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # روابط
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="content_items")
    
    __table_args__ = (
        Index('idx_content_lesson_order', 'lesson_id', 'order'),
        {'sqlite_autoincrement': True}
    )
    
    def __repr__(self):
        return f"<ContentItem(id={self.id}, lesson_id={self.lesson_id}, type='{self.content_type}')>"


# ============================================================================
# Enrollment & Progress Models
# ============================================================================

class Enrollment(Base):
    """
    ثبت‌نام کاربران در دوره‌ها
    """
    __tablename__ = "education_enrollments"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("education_courses.id"), nullable=False)
    
    # وضعیت
    status: Mapped[str] = mapped_column(SQLEnum(EnrollmentStatus), default=EnrollmentStatus.ACTIVE)
    
    # پرداخت
    payment_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("payments.id"), nullable=True)
    enrollment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expiry_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # پیشرفت
    progress_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    completed_lessons_count: Mapped[int] = mapped_column(Integer, default=0)
    total_lessons_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # آخرین فعالیت
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # نمرات
    final_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # روابط
    user: Mapped["User"] = relationship("User", back_populates="enrollments")
    course: Mapped["Course"] = relationship("Course", back_populates="enrollments")
    progress_records: Mapped[List["LearningProgress"]] = relationship(
        "LearningProgress", back_populates="enrollment", cascade="all, delete-orphan"
    )
    certificate: Mapped["Certificate"] = relationship(
        "Certificate", back_populates="enrollment", uselist=False
    )
    
    __table_args__ = (
        # یکتایی جفت کاربر-دوره
        Index('idx_enrollment_user_course', 'user_id', 'course_id', unique=True),
        Index('idx_enrollment_status', 'status'),
        {'sqlite_autoincrement': True}
    )
    
    def __repr__(self):
        return f"<Enrollment(user={self.user_id}, course={self.course_id}, status='{self.status}')>"


class LearningProgress(Base):
    """
    پیشرفت یادگیری برای هر درس
    """
    __tablename__ = "education_learning_progress"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    enrollment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("education_enrollments.id"), nullable=False
    )
    lesson_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("education_lessons.id"), nullable=False
    )
    
    # وضعیت
    status: Mapped[str] = mapped_column(
        SQLEnum("not_started", "in_progress", "completed", name="progress_status"),
        default="not_started"
    )
    
    # پیشرفت محتوا
    progress_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    current_content_item_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("education_content_items.id"), nullable=True
    )
    
    # زمان‌بندی
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    time_spent_seconds: Mapped[int] = mapped_column(Integer, default=0)
    
    # نمرات (برای آزمون‌ها)
    quiz_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    quiz_attempts: Mapped[int] = mapped_column(Integer, default=0)
    
    # یادداشت‌های کاربر
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bookmarks: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # روابط
    enrollment: Mapped["Enrollment"] = relationship("Enrollment", back_populates="progress_records")
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="progress_records")
    current_content_item: Mapped["ContentItem"] = relationship("ContentItem")
    
    __table_args__ = (
        Index('idx_progress_enrollment_lesson', 'enrollment_id', 'lesson_id', unique=True),
        {'sqlite_autoincrement': True}
    )
    
    def __repr__(self):
        return f"<LearningProgress(enrollment={self.enrollment_id}, lesson={self.lesson_id}, status='{self.status}')>"


# ============================================================================
# Quiz & Assessment Models
# ============================================================================

class Quiz(Base):
    """
    آزمون‌ها و ارزیابی‌ها
    """
    __tablename__ = "education_quizzes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("education_courses.id"), nullable=False)
    
    # اطلاعات آزمون
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    title_fa: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # تنظیمات
    time_limit_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    passing_score: Mapped[float] = mapped_column(Float, default=70.0)  # درصد قبولی
    max_attempts: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # None = نامحدود
    
    # تصادفی‌سازی
    shuffle_questions: Mapped[bool] = mapped_column(Boolean, default=True)
    shuffle_answers: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # نمایش نتایج
    show_correct_answers: Mapped[bool] = mapped_column(Boolean, default=True)
    show_score_immediately: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # دسترسی
    available_from: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    available_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # وزن در نمره نهایی
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # روابط
    course: Mapped["Course"] = relationship("Course", back_populates="quizzes")
    questions: Mapped[List["QuizQuestion"]] = relationship(
        "QuizQuestion", back_populates="quiz", cascade="all, delete-orphan"
    )
    attempts: Mapped[List["QuizAttempt"]] = relationship(
        "QuizAttempt", back_populates="quiz", cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Quiz(id={self.id}, course_id={self.course_id}, title='{self.title}')>"


class QuizQuestion(Base):
    """
    سوالات آزمون
    """
    __tablename__ = "education_quiz_questions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quiz_id: Mapped[int] = mapped_column(Integer, ForeignKey("education_quizzes.id"), nullable=False)
    
    # سوال
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_text_fa: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # نوع سوال
    question_type: Mapped[str] = mapped_column(
        SQLEnum(
            "multiple_choice", "true_false", "short_answer", 
            "essay", "matching", "fill_blank", name="question_type"
        ),
        nullable=False
    )
    
    # پاسخ‌ها (برای سوالات چندگزینه‌ای)
    answers: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    # ساختار: [{"text": "...", "is_correct": true, "feedback": "..."}, ...]
    
    # پاسخ صحیح (برای سایر انواع)
    correct_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # نمره
    points: Mapped[float] = mapped_column(Float, default=1.0)
    
    # توضیحات
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # ترتیب
    order: Mapped[int] = mapped_column(Integer, default=0)
    
    # متادیتا
    difficulty: Mapped[str] = mapped_column(
        SQLEnum("easy", "medium", "hard", name="question_difficulty"),
        default="medium"
    )
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # روابط
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="questions")
    
    __table_args__ = (
        Index('idx_question_quiz_order', 'quiz_id', 'order'),
        {'sqlite_autoincrement': True}
    )
    
    def __repr__(self):
        return f"<QuizQuestion(id={self.id}, quiz_id={self.quiz_id}, type='{self.question_type}')>"


class QuizAttempt(Base):
    """
    تلاش‌های کاربر برای آزمون
    """
    __tablename__ = "education_quiz_attempts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    quiz_id: Mapped[int] = mapped_column(Integer, ForeignKey("education_quizzes.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    enrollment_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("education_enrollments.id"), nullable=True
    )
    
    # وضعیت
    status: Mapped[str] = mapped_column(
        SQLEnum("in_progress", "submitted", "graded", name="attempt_status"),
        default="in_progress"
    )
    
    # پاسخ‌ها
    answers: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    # ساختار: {"question_id": "answer", ...}
    
    # نمرات
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # زمان‌بندی
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    time_taken_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # بازخورد
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    graded_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    graded_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # روابط
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="attempts")
    user: Mapped["User"] = relationship("User")
    enrollment: Mapped["Enrollment"] = relationship("Enrollment")
    
    __table_args__ = (
        Index('idx_attempt_quiz_user', 'quiz_id', 'user_id'),
        {'sqlite_autoincrement': True}
    )
    
    def __repr__(self):
        return f"<QuizAttempt(id={self.id}, quiz={self.quiz_id}, user={self.user_id}, score={self.score})>"


# ============================================================================
# Certificate Models
# ============================================================================

class Certificate(Base):
    """
    گواهینامه‌های پایان دوره
    """
    __tablename__ = "education_certificates"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    enrollment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("education_enrollments.id"), nullable=False, unique=True
    )
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("education_courses.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    
    # مشخصات گواهینامه
    certificate_number: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    title_fa: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # وضعیت
    status: Mapped[str] = mapped_column(SQLEnum(CertificateStatus), default=CertificateStatus.PENDING)
    
    # تاریخ‌ها
    issued_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    revoke_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # نمره نهایی
    final_score: Mapped[float] = mapped_column(Float, nullable=False)
    
    # امضاها
    instructor_signature: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    organization_signature: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # فایل
    pdf_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    verification_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # متادیتا
    extra_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # روابط
    enrollment: Mapped["Enrollment"] = relationship("Enrollment", back_populates="certificate")
    course: Mapped["Course"] = relationship("Course", back_populates="certificates")
    user: Mapped["User"] = relationship("User")
    
    __table_args__ = (
        Index('idx_certificate_number', 'certificate_number'),
        Index('idx_certificate_user', 'user_id'),
        {'sqlite_autoincrement': True}
    )
    
    def __repr__(self):
        return f"<Certificate(id={self.id}, number='{self.certificate_number}', user={self.user_id})>"


# ============================================================================
# Additional Models
# ============================================================================

class CourseReview(Base):
    """
    نظرات و امتیازات کاربران به دوره‌ها
    """
    __tablename__ = "education_course_reviews"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("education_courses.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    enrollment_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("education_enrollments.id"), nullable=True
    )
    
    # امتیاز
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    
    # نظر
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # وضعیت
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified_purchase: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # واکنش‌ها
    helpful_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # پاسخ مدرس
    instructor_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    instructor_response_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    __table_args__ = (
        Index('idx_review_course_user', 'course_id', 'user_id', unique=True),
        {'sqlite_autoincrement': True}
    )
    
    def __repr__(self):
        return f"<CourseReview(course={self.course_id}, user={self.user_id}, rating={self.rating})>"


class LearningPath(Base):
    """
    مسیرهای یادگیری (مجموعه‌ای از دوره‌های مرتبط)
    """
    __tablename__ = "education_learning_paths"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # اطلاعات مسیر
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    title_fa: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # وضعیت
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # مدت تخمینی
    estimated_hours: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # ترتیب دوره‌ها
    courses_order: Mapped[Optional[List[int]]] = mapped_column(JSON, nullable=True)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<LearningPath(id={self.id}, title='{self.title}')>"


# Import User model reference for relationships
# This will be resolved at runtime when the models are loaded
User = type("User", (), {})  # Placeholder, will be replaced by actual User model
