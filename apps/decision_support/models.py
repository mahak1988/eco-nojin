"""
Database Models for Decision Support Module
مدل‌های پایگاه داده برای ماژول تصمیم‌یار

این ماژول شامل مدل‌های SQLAlchemy برای:
- معیارهای تصمیم‌گیری (Criteria)
- گزینه‌ها (Alternatives)
- ماتریس تصمیم (Decision Matrix)
- نتایج تحلیل (Analysis Results)
- پروفایل‌های تصمیم‌گیری (Decision Profiles)
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, 
    Text, Boolean, JSON, Numeric, Enum as SQLEnum, Table
)
from sqlalchemy.orm import relationship, declarative_base, Mapped, mapped_column
from sqlalchemy.sql import func

Base = declarative_base()


class CriterionType(str, Enum):
    """انواع معیارهای تصمیم‌گیری"""
    BENEFIT = "benefit"  # معیار سود - مقدار بیشتر بهتر است
    COST = "cost"        # معیار هزینه - مقدار کمتر بهتر است
    QUALITATIVE = "qualitative"  # معیار کیفی


class MCDMMethod(str, Enum):
    """روش‌های تصمیم‌گیری چندمعیاره پشتیبانی‌شده"""
    AHP = "ahp"                  # فرآیند تحلیل سلسله‌مراتبی
    TOPSIS = "topsis"            # تکنیک ترتیب‌دهی بر اساس شباهت به راه‌حل ایده‌آل
    PROMETHEE = "promethee"      # روش خروج رتبه‌بندی غنی‌سازی ارزیابی
    ELECTRE = "electre"          # روش حذف و انتخاب ترجمه واقعیت
    SAW = "saw"                  # میانگین وزنی ساده
    VIKOR = "vikor"              # راه‌حل سازشی بهینه‌سازی چندمعیاره
    ANP = "anp"                  # فرآیند تحلیل شبکه‌ای
    DEMATEL = "dematel"          # آزمایشگاه و ارزیابی تصمیم


class DecisionProject(Base):
    """
    پروژه تصمیم‌گیری
    هر پروژه می‌تواند شامل چندین تحلیل با روش‌های مختلف باشد
    """
    __tablename__ = "decision_projects"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # وضعیت پروژه
    status: Mapped[str] = mapped_column(
        SQLEnum("draft", "active", "completed", "archived", name="project_status"),
        default="draft"
    )
    
    # زمینه و دامنه کاربرد
    domain: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g., agriculture, energy, finance
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # کاربر ایجادکننده
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # روابط
    criteria: Mapped[List["DecisionCriterion"]] = relationship(
        "DecisionCriterion", back_populates="project", cascade="all, delete-orphan"
    )
    alternatives: Mapped[List["DecisionAlternative"]] = relationship(
        "DecisionAlternative", back_populates="project", cascade="all, delete-orphan"
    )
    analyses: Mapped[List["DecisionAnalysis"]] = relationship(
        "DecisionAnalysis", back_populates="project", cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<DecisionProject(id={self.id}, title='{self.title}', status='{self.status}')>"


class DecisionCriterion(Base):
    """
    معیارهای تصمیم‌گیری
    هر معیار دارای وزن و نوع مشخص است
    """
    __tablename__ = "decision_criteria"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("decision_projects.id"), nullable=False)
    
    # اطلاعات معیار
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # کد کوتاه برای ارجاع
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # نوع معیار
    criterion_type: Mapped[str] = mapped_column(
        SQLEnum(CriterionType),
        default=CriterionType.BENEFIT
    )
    
    # وزن معیار (در روش‌هایی مثل AHP محاسبه می‌شود)
    weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # واحد اندازه‌گیری
    unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # محدوده مقادیر قابل قبول
    min_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # متادیتای اضافی
    extra_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # روابط
    project: Mapped["DecisionProject"] = relationship("DecisionProject", back_populates="criteria")
    sub_criteria: Mapped[List["DecisionCriterion"]] = relationship(
        "DecisionCriterion",
        backref="parent_criterion",
        remote_side=[id],
        foreign_keys=[ForeignKey("decision_criteria.id")]
    )
    
    __table_args__ = (
        # یکتایی کد در هر پروژه
        {'sqlite_autoincrement': True}
    )
    
    def __repr__(self):
        return f"<DecisionCriterion(id={self.id}, name='{self.name}', weight={self.weight})>"


class DecisionAlternative(Base):
    """
    گزینه‌های تصمیم‌گیری
    هر گزینه دارای امتیازات مختلف در معیارهای گوناگون است
    """
    __tablename__ = "decision_alternatives"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("decision_projects.id"), nullable=False)
    
    # اطلاعات گزینه
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # وضعیت گزینه
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # متادیتا و اطلاعات تکمیلی
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    extra_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # روابط
    project: Mapped["DecisionProject"] = relationship("DecisionProject", back_populates="alternatives")
    evaluations: Mapped[List["DecisionEvaluation"]] = relationship(
        "DecisionEvaluation", back_populates="alternative", cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<DecisionAlternative(id={self.id}, name='{self.name}')>"


class DecisionEvaluation(Base):
    """
    ماتریس تصمیم (ارزیابی گزینه‌ها در معیارها)
    هر رکورد نشان‌دهنده امتیاز یک گزینه در یک معیار خاص است
    """
    __tablename__ = "decision_evaluations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # کلیدهای خارجی
    alternative_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("decision_alternatives.id"), nullable=False
    )
    criterion_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("decision_criteria.id"), nullable=False
    )
    
    # مقدار ارزیابی
    value: Mapped[float] = mapped_column(Numeric(20, 6), nullable=False)
    
    # منبع داده (اختیاری)
    data_source: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    confidence_level: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-1
    
    # یادداشت‌ها
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # روابط
    alternative: Mapped["DecisionAlternative"] = relationship(
        "DecisionAlternative", back_populates="evaluations"
    )
    criterion: Mapped["DecisionCriterion"] = relationship("DecisionCriterion")
    
    __table_args__ = (
        # یکتایی جفت گزینه-معیار
        {'sqlite_autoincrement': True}
    )
    
    def __repr__(self):
        return f"<DecisionEvaluation(alt={self.alternative_id}, crit={self.criterion_id}, value={self.value})>"


class DecisionAnalysis(Base):
    """
    نتایج تحلیل تصمیم‌گیری
    هر تحلیل با یک روش خاص (AHP, TOPSIS, etc.) انجام شده است
    """
    __tablename__ = "decision_analyses"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("decision_projects.id"), nullable=False)
    
    # روش تحلیل
    method: Mapped[str] = mapped_column(SQLEnum(MCDMMethod), nullable=False)
    
    # عنوان و توضیحات
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # پارامترهای روش
    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # نتایج
    results: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    rankings: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # تحلیل حساسیت
    sensitivity_analysis: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # وضعیت
    status: Mapped[str] = mapped_column(
        SQLEnum("pending", "running", "completed", "failed", name="analysis_status"),
        default="pending"
    )
    
    # خطاها (در صورت شکست)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # روابط
    project: Mapped["DecisionProject"] = relationship("DecisionProject", back_populates="analyses")
    
    def __repr__(self):
        return f"<DecisionAnalysis(id={self.id}, method='{self.method}', status='{self.status}')>"


class ComparisonMatrix(Base):
    """
    ماتریس مقایسات زوجی (برای روش AHP و ANP)
    """
    __tablename__ = "comparison_matrices"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # پروژه یا تحلیل مرتبط
    project_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("decision_projects.id"), nullable=True
    )
    analysis_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("decision_analyses.id"), nullable=True
    )
    
    # نوع مقایسه
    matrix_type: Mapped[str] = mapped_column(
        SQLEnum("criteria", "alternatives_per_criterion", name="matrix_type"),
        nullable=False
    )
    
    # معیار والد (برای مقایسات زیرمعیارها یا گزینه‌ها)
    parent_criterion_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("decision_criteria.id"), nullable=True
    )
    
    # داده‌های ماتریس به صورت JSON
    # ساختار: {"C1": {"C1": 1.0, "C2": 3.0, ...}, "C2": {...}, ...}
    matrix_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    
    # شاخص ناسازگاری (Consistency Ratio)
    consistency_ratio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_consistent: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    def __repr__(self):
        return f"<ComparisonMatrix(id={self.id}, type='{self.matrix_type}', CR={self.consistency_ratio})>"


class DecisionTemplate(Base):
    """
    قالب‌های از پیش تعریف‌شده برای پروژه‌های تصمیم‌گیری
    برای تسریع ایجاد پروژه‌های مشابه
    """
    __tablename__ = "decision_templates"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # اطلاعات قالب
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    domain: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # معیارهای پیش‌فرض
    default_criteria: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # روش پیشنهادی
    recommended_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # متادیتا
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<DecisionTemplate(id={self.id}, name='{self.name}')>"


# جدول ارتباطی برای گروه‌بندی معیارها
criterion_groups = Table(
    'criterion_group_criteria',  # renamed to avoid conflict with CriterionGroup table
    Base.metadata,
    Column('criterion_id', Integer, ForeignKey('decision_criteria.id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('criterion_groups.id'), primary_key=True)
)


class CriterionGroup(Base):
    """
    گروه‌بندی معیارها برای سازماندهی بهتر
    """
    __tablename__ = "criterion_groups"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("decision_projects.id"), nullable=False)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # وزن گروه (اختیاری)
    weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # روابط
    criteria: Mapped[List["DecisionCriterion"]] = relationship(
        "DecisionCriterion", secondary=criterion_groups, back_populates="groups"
    )
    
    def __repr__(self):
        return f"<CriterionGroup(id={self.id}, name='{self.name}')>"


# اضافه کردن رابطه معکوس به DecisionCriterion
DecisionCriterion.groups = relationship(
    "CriterionGroup",
    secondary=criterion_groups,
    back_populates="criteria"
)
