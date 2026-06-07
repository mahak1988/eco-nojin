# api/modules/library/models.py
"""
مدل‌های کتابخانه دیجیتال علمی-پژوهشی
نسخه 2.0 - با سیستم تایید و دانشنامه کهن
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey, Text, Enum as SQLEnum, Table, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from api.core.database import Base
import enum


# ============================================================
# Enums
# ============================================================
class PublicationType(enum.Enum):
    ARTICLE = "article"
    BOOK = "book"
    THESIS = "thesis"
    REPORT = "report"
    VIDEO = "video"
    STANDARD = "standard"
    CONFERENCE = "conference"


class PublicationStatus(enum.Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    PUBLISHED = "published"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class ApprovalStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class UserRole(enum.Enum):
    RESEARCHER = "researcher"
    REVIEWER = "reviewer"
    EDITOR = "editor"
    ADMIN = "admin"
    LIBRARIAN = "librarian"


# ============================================================
# Association Tables
# ============================================================
publication_authors = Table(
    "publication_authors", Base.metadata,
    Column("publication_id", Integer, ForeignKey("publications.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("author_order", Integer, default=1),
    Column("is_corresponding", Boolean, default=False),
)

publication_keywords = Table(
    "publication_keywords", Base.metadata,
    Column("publication_id", Integer, ForeignKey("publications.id"), primary_key=True),
    Column("keyword_id", Integer, ForeignKey("keywords.id"), primary_key=True),
)


# ============================================================
# Core Models
# ============================================================
class User(Base):
    """کاربران سیستم"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    full_name = Column(String(200), nullable=False)
    affiliation = Column(String(300))
    orcid_id = Column(String(50), unique=True)
    
    role = Column(SQLEnum(UserRole), default=UserRole.RESEARCHER)
    is_verified = Column(Boolean, default=False)
    
    total_publications = Column(Integer, default=0)
    total_citations = Column(Integer, default=0)
    h_index = Column(Integer, default=0)
    
    bio = Column(Text)
    research_interests = Column(JSON)
    profile_image_url = Column(String(500))
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class Keyword(Base):
    """کلمات کلیدی"""
    __tablename__ = "keywords"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    name_en = Column(String(200), unique=True)
    description = Column(Text)


class Publication(Base):
    """منابع علمی"""
    __tablename__ = "publications"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(1000), nullable=False)
    title_en = Column(String(1000))
    
    publication_type = Column(SQLEnum(PublicationType), nullable=False)
    status = Column(SQLEnum(PublicationStatus), default=PublicationStatus.DRAFT)
    
    abstract = Column(Text, nullable=False)
    abstract_en = Column(Text)
    full_text_url = Column(String(500))
    pdf_url = Column(String(500))
    doi = Column(String(100), unique=True, index=True)
    
    journal_name = Column(String(300))
    publisher = Column(String(300))
    publication_date = Column(DateTime)
    
    # تصویر
    cover_image_url = Column(String(500))
    thumbnail_url = Column(String(500))
    
    # موقعیت جغرافیایی
    study_location_name = Column(String(300))
    study_location_lat = Column(Float)
    study_location_lon = Column(Float)
    study_location_radius_km = Column(Float, default=10)
    
    # متادیتا
    language = Column(String(10), default="fa")
    license_type = Column(String(100), default="CC-BY-NC-SA")
    access_level = Column(String(20), default="public")
    
    # آمار
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    citation_count = Column(Integer, default=0)
    rating_average = Column(Float, default=0)
    
    # کیفیت
    quality_score = Column(Float, default=0)
    
    # تاریخ‌ها
    submitted_at = Column(DateTime, server_default=func.now())
    published_at = Column(DateTime)
    
    # سیستم تایید
    approval_status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING)
    approved_by_id = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime)
    rejection_reason = Column(Text)
    
    authors = relationship("User", secondary=publication_authors)
    keywords = relationship("Keyword", secondary=publication_keywords)


class ResearchLocation(Base):
    """مکان‌های تحقیقاتی روی نقشه"""
    __tablename__ = "research_locations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(300), nullable=False)
    name_en = Column(String(300))
    description = Column(Text)
    
    # موقعیت
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius_km = Column(Float, default=10)
    
    # تصویر
    image_url = Column(String(500))
    thumbnail_url = Column(String(500))
    
    # اطلاعات
    research_topics = Column(JSON)  # لیست موضوعات
    publication_count = Column(Integer, default=0)
    
    # سیستم تایید
    approval_status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING)
    submitted_by_id = Column(Integer, ForeignKey("users.id"))
    approved_by_id = Column(Integer, ForeignKey("users.id"))
    
    # تاریخ‌ها
    created_at = Column(DateTime, server_default=func.now())
    approved_at = Column(DateTime)
    
    # روابط
    submitter = relationship("User", foreign_keys=[submitted_by_id])
    approver = relationship("User", foreign_keys=[approved_by_id])


class ResearchGroup(Base):
    """گروه‌های تحقیقاتی"""
    __tablename__ = "research_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(300), nullable=False)
    name_en = Column(String(300))
    description = Column(Text)
    
    # تصویر
    cover_image_url = Column(String(500))
    logo_url = Column(String(500))
    
    # موضوعات
    research_areas = Column(JSON)
    
    # اعضا
    leader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    max_members = Column(Integer, default=50)
    current_members = Column(Integer, default=1)
    
    # وضعیت
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)
    
    # سیستم تایید
    approval_status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING)
    submitted_by_id = Column(Integer, ForeignKey("users.id"))
    approved_by_id = Column(Integer, ForeignKey("users.id"))
    rejection_reason = Column(Text)
    
    # تاریخ‌ها
    created_at = Column(DateTime, server_default=func.now())
    approved_at = Column(DateTime)
    
    # روابط
    leader = relationship("User", foreign_keys=[leader_id])
    submitter = relationship("User", foreign_keys=[submitted_by_id])
    approver = relationship("User", foreign_keys=[approved_by_id])


class ResearchChallenge(Base):
    """چالش‌های پژوهشی"""
    __tablename__ = "research_challenges"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    title_en = Column(String(500))
    description = Column(Text, nullable=False)
    
    # تصویر
    cover_image_url = Column(String(500))
    thumbnail_url = Column(String(500))
    
    # موضوع
    research_area = Column(String(200))
    difficulty_level = Column(String(50), default="intermediate")
    
    # زمان‌بندی
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    # جوایز
    prize_description = Column(Text)
    prize_amount = Column(Float)
    prize_currency = Column(String(10), default="IRR")
    
    # معیارها
    evaluation_criteria = Column(JSON)
    
    # وضعیت
    status = Column(String(50), default="upcoming")
    is_public = Column(Boolean, default=True)
    
    # سیستم تایید
    approval_status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING)
    submitted_by_id = Column(Integer, ForeignKey("users.id"))
    approved_by_id = Column(Integer, ForeignKey("users.id"))
    rejection_reason = Column(Text)
    
    # آمار
    participant_count = Column(Integer, default=0)
    submission_count = Column(Integer, default=0)
    
    # تاریخ‌ها
    created_at = Column(DateTime, server_default=func.now())
    approved_at = Column(DateTime)
    
    # روابط
    submitter = relationship("User", foreign_keys=[submitted_by_id])
    approver = relationship("User", foreign_keys=[approved_by_id])


# ============================================================
# دانشنامه کهن
# ============================================================
class AncientKnowledge(Base):
    """دانشنامه کهن - دانش سنتی و بومی"""
    __tablename__ = "ancient_knowledge"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    title_en = Column(String(500))
    
    # محتوا
    description = Column(Text, nullable=False)
    content = Column(Text)  # محتوای کامل
    
    # دسته‌بندی
    category = Column(String(100))  # agriculture, water_management, medicine, etc.
    subcategory = Column(String(100))
    tags = Column(JSON)  # برچسب‌ها
    
    # موقعیت جغرافیایی (منشاء دانش)
    origin_location = Column(String(300))
    origin_latitude = Column(Float)
    origin_longitude = Column(Float)
    
    # تصویر
    cover_image_url = Column(String(500))
    gallery_images = Column(JSON)  # لیست تصاویر
    
    # منابع
    sources = Column(JSON)  # لیست منابع
    references = Column(Text)
    
    # اطلاعات تاریخی
    historical_period = Column(String(200))
    century = Column(String(50))
    civilization = Column(String(200))
    
    # زبان
    original_language = Column(String(50))
    language = Column(String(10), default="fa")
    
    # وضعیت
    is_verified = Column(Boolean, default=False)
    verified_by_id = Column(Integer, ForeignKey("users.id"))
    verified_at = Column(DateTime)
    
    # سیستم تایید
    approval_status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING)
    submitted_by_id = Column(Integer, ForeignKey("users.id"))
    approved_by_id = Column(Integer, ForeignKey("users.id"))
    rejection_reason = Column(Text)
    
    # آمار
    view_count = Column(Integer, default=0)
    rating_average = Column(Float, default=0)
    rating_count = Column(Integer, default=0)
    
    # تاریخ‌ها
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    approved_at = Column(DateTime)
    
    # روابط
    submitter = relationship("User", foreign_keys=[submitted_by_id])
    approver = relationship("User", foreign_keys=[approved_by_id])
    verifier = relationship("User", foreign_keys=[verified_by_id])


class AncientKnowledgeCategory(Base):
    """دسته‌بندی‌های دانشنامه کهن"""
    __tablename__ = "ancient_knowledge_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    name_en = Column(String(200), unique=True)
    description = Column(Text)
    icon = Column(String(50))  # نام آیکون
    color = Column(String(20))  # کد رنگ
    
    parent_id = Column(Integer, ForeignKey("ancient_knowledge_categories.id"))
    
    knowledge_count = Column(Integer, default=0)
