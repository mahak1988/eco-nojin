"""
Pydantic Schemas for Decision Support Module
اسکیماهای Pydantic برای ماژول تصمیم‌یار

این فایل شامل:
- Schemaهای درخواست (Request)
- Schemaهای پاسخ (Response)
- Schemaهای میانی برای اعتبارسنجی داده‌ها
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Enums
# ============================================================================

class CriterionType(str, Enum):
    """انواع معیارهای تصمیم‌گیری"""
    BENEFIT = "benefit"
    COST = "cost"
    QUALITATIVE = "qualitative"


class MCDMMethod(str, Enum):
    """روش‌های تصمیم‌گیری چندمعیاره"""
    AHP = "ahp"
    TOPSIS = "topsis"
    PROMETHEE = "promethee"
    ELECTRE = "electre"
    SAW = "saw"
    VIKOR = "vikor"
    ANP = "anp"
    DEMATEL = "dematel"


class ProjectStatus(str, Enum):
    """وضعیت پروژه"""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class AnalysisStatus(str, Enum):
    """وضعیت تحلیل"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# ============================================================================
# Base Schemas
# ============================================================================

class BaseSchema(BaseModel):
    """پایه تمام اسکیماها با تنظیمات مشترک"""
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Decision Project Schemas
# ============================================================================

class DecisionProjectBase(BaseSchema):
    """اسکیمای پایه پروژه تصمیم‌گیری"""
    title: str = Field(..., min_length=1, max_length=255, description="عنوان پروژه")
    description: Optional[str] = Field(None, max_length=5000, description="توضیحات پروژه")
    domain: Optional[str] = Field(None, max_length=100, description="دامنه کاربرد")
    status: ProjectStatus = Field(default=ProjectStatus.DRAFT)
    context: Optional[Dict[str, Any]] = Field(None, description="زمینه و متادیتای پروژه")


class DecisionProjectCreate(DecisionProjectBase):
    """اسکیمای ایجاد پروژه جدید"""
    pass


class DecisionProjectUpdate(BaseModel):
    """اسکیمای به‌روزرسانی پروژه (همه فیلدها اختیاری)"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    domain: Optional[str] = Field(None, max_length=100)
    status: Optional[ProjectStatus] = None
    context: Optional[Dict[str, Any]] = None


class DecisionProjectResponse(DecisionProjectBase):
    """اسکیمای پاسخ پروژه"""
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    # آمار خلاصه
    criteria_count: Optional[int] = 0
    alternatives_count: Optional[int] = 0
    analyses_count: Optional[int] = 0


class DecisionProjectListResponse(BaseSchema):
    """لیست پروژه‌ها با صفحه‌بندی"""
    items: List[DecisionProjectResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# Decision Criterion Schemas
# ============================================================================

class DecisionCriterionBase(BaseSchema):
    """اسکیمای پایه معیار"""
    name: str = Field(..., min_length=1, max_length=255, description="نام معیار")
    code: Optional[str] = Field(None, max_length=50, description="کد کوتاه معیار")
    description: Optional[str] = Field(None, max_length=2000, description="توضیحات معیار")
    criterion_type: CriterionType = Field(default=CriterionType.BENEFIT)
    weight: Optional[float] = Field(None, ge=0, le=1, description="وزن معیار")
    unit: Optional[str] = Field(None, max_length=50, description="واحد اندازه‌گیری")
    min_value: Optional[float] = Field(None, description="حداقل مقدار قابل قبول")
    max_value: Optional[float] = Field(None, description="حداکثر مقدار قابل قبول")
    metadata: Optional[Dict[str, Any]] = Field(None, description="متادیتای اضافی")


class DecisionCriterionCreate(DecisionCriterionBase):
    """اسکیمای ایجاد معیار جدید"""
    project_id: int
    parent_criterion_id: Optional[int] = Field(None, description="آیدی معیار والد برای سلسله مراتب")


class DecisionCriterionUpdate(BaseModel):
    """اسکیمای به‌روزرسانی معیار"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=2000)
    criterion_type: Optional[CriterionType] = None
    weight: Optional[float] = Field(None, ge=0, le=1)
    unit: Optional[str] = Field(None, max_length=50)
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class DecisionCriterionResponse(DecisionCriterionBase):
    """اسکیمای پاسخ معیار"""
    id: int
    project_id: int
    created_at: datetime
    
    # زیرمعیارها
    sub_criteria: Optional[List["DecisionCriterionResponse"]] = None


class DecisionCriterionListResponse(BaseSchema):
    """لیست معیارها"""
    items: List[DecisionCriterionResponse]
    total: int


# ============================================================================
# Decision Alternative Schemas
# ============================================================================

class DecisionAlternativeBase(BaseSchema):
    """اسکیمای پایه گزینه"""
    name: str = Field(..., min_length=1, max_length=255, description="نام گزینه")
    code: Optional[str] = Field(None, max_length=50, description="کد کوتاه گزینه")
    description: Optional[str] = Field(None, max_length=2000, description="توضیحات گزینه")
    is_active: bool = Field(default=True, description="فعال بودن گزینه")
    category: Optional[str] = Field(None, max_length=100, description="دسته‌بندی گزینه")
    metadata: Optional[Dict[str, Any]] = Field(None, description="متادیتای اضافی")


class DecisionAlternativeCreate(DecisionAlternativeBase):
    """اسکیمای ایجاد گزینه جدید"""
    project_id: int


class DecisionAlternativeUpdate(BaseModel):
    """اسکیمای به‌روزرسانی گزینه"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=2000)
    is_active: Optional[bool] = None
    category: Optional[str] = Field(None, max_length=100)
    metadata: Optional[Dict[str, Any]] = None


class DecisionAlternativeResponse(DecisionAlternativeBase):
    """اسکیمای پاسخ گزینه"""
    id: int
    project_id: int
    created_at: datetime


class DecisionAlternativeListResponse(BaseSchema):
    """لیست گزینه‌ها"""
    items: List[DecisionAlternativeResponse]
    total: int


# ============================================================================
# Decision Evaluation Schemas (ماتریس تصمیم)
# ============================================================================

class DecisionEvaluationBase(BaseSchema):
    """اسکیمای پایه ارزیابی"""
    value: float = Field(..., description="مقدار ارزیابی")
    data_source: Optional[str] = Field(None, max_length=255, description="منبع داده")
    confidence_level: Optional[float] = Field(None, ge=0, le=1, description="سطح اطمینان")
    notes: Optional[str] = Field(None, max_length=2000, description="یادداشت‌ها")


class DecisionEvaluationCreate(DecisionEvaluationBase):
    """اسکیمای ایجاد ارزیابی جدید"""
    alternative_id: int
    criterion_id: int


class DecisionEvaluationUpdate(BaseModel):
    """اسکیمای به‌روزرسانی ارزیابی"""
    value: Optional[float] = None
    data_source: Optional[str] = Field(None, max_length=255)
    confidence_level: Optional[float] = Field(None, ge=0, le=1)
    notes: Optional[str] = Field(None, max_length=2000)


class DecisionEvaluationResponse(DecisionEvaluationBase):
    """اسکیمای پاسخ ارزیابی"""
    id: int
    alternative_id: int
    criterion_id: int
    created_at: datetime
    updated_at: datetime
    
    # اطلاعات مرتبط (اختیاری)
    alternative_name: Optional[str] = None
    criterion_name: Optional[str] = None


class DecisionMatrixCreate(BaseModel):
    """اسکیمای ایجاد ماتریس تصمیم کامل"""
    project_id: int
    evaluations: List[DecisionEvaluationCreate] = Field(
        ..., 
        min_length=1,
        description="لیست ارزیابی‌ها برای پر کردن ماتریس"
    )


class DecisionMatrixResponse(BaseSchema):
    """پاسخ ماتریس تصمیم"""
    project_id: int
    criteria_count: int
    alternatives_count: int
    evaluations_count: int
    matrix: Dict[str, Dict[str, float]] = Field(
        ..., 
        description="ماتریس به صورت تو در تو: {criterion_code: {alternative_code: value}}"
    )


# ============================================================================
# Decision Analysis Schemas
# ============================================================================

class DecisionAnalysisBase(BaseSchema):
    """اسکیمای پایه تحلیل"""
    method: MCDMMethod = Field(..., description="روش تحلیل")
    title: str = Field(..., min_length=1, max_length=255, description="عنوان تحلیل")
    description: Optional[str] = Field(None, max_length=5000, description="توضیحات تحلیل")
    parameters: Optional[Dict[str, Any]] = Field(None, description="پارامترهای روش")


class DecisionAnalysisCreate(DecisionAnalysisBase):
    """اسکیمای ایجاد تحلیل جدید"""
    project_id: int


class DecisionAnalysisUpdate(BaseModel):
    """اسکیمای به‌روزرسانی تحلیل"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    parameters: Optional[Dict[str, Any]] = None
    status: Optional[AnalysisStatus] = None


class RankingItem(BaseSchema):
    """آیتم رتبه‌بندی"""
    alternative_id: int
    alternative_name: str
    rank: int
    score: float
    details: Optional[Dict[str, Any]] = None


class DecisionAnalysisResponse(DecisionAnalysisBase):
    """اسکیمای پاسخ تحلیل"""
    id: int
    project_id: int
    status: AnalysisStatus
    results: Optional[Dict[str, Any]] = None
    rankings: Optional[List[RankingItem]] = None
    sensitivity_analysis: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class DecisionAnalysisListResponse(BaseSchema):
    """لیست تحلیل‌ها"""
    items: List[DecisionAnalysisResponse]
    total: int


# ============================================================================
# Comparison Matrix Schemas (برای AHP/ANP)
# ============================================================================

class ComparisonMatrixBase(BaseSchema):
    """اسکیمای پایه ماتریس مقایسات زوجی"""
    matrix_type: str = Field(..., description="نوع ماتریس: criteria یا alternatives_per_criterion")
    matrix_data: Dict[str, Any] = Field(..., description="داده‌های ماتریس")


class ComparisonMatrixCreate(ComparisonMatrixBase):
    """اسکیمای ایجاد ماتریس مقایسه"""
    project_id: Optional[int] = None
    analysis_id: Optional[int] = None
    parent_criterion_id: Optional[int] = None


class ComparisonMatrixUpdate(BaseModel):
    """اسکیمای به‌روزرسانی ماتریس مقایسه"""
    matrix_data: Optional[Dict[str, Any]] = None


class ComparisonMatrixResponse(ComparisonMatrixBase):
    """اسکیمای پاسخ ماتریس مقایسه"""
    id: int
    project_id: Optional[int] = None
    analysis_id: Optional[int] = None
    parent_criterion_id: Optional[int] = None
    consistency_ratio: Optional[float] = None
    is_consistent: Optional[bool] = None
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Decision Template Schemas
# ============================================================================

class DecisionTemplateBase(BaseSchema):
    """اسکیمای پایه قالب"""
    name: str = Field(..., min_length=1, max_length=255, description="نام قالب")
    description: Optional[str] = Field(None, max_length=2000, description="توضیحات قالب")
    domain: Optional[str] = Field(None, max_length=100, description="دامنه کاربرد")
    default_criteria: Optional[List[Dict[str, Any]]] = Field(None, description="معیارهای پیش‌فرض")
    recommended_method: Optional[MCDMMethod] = Field(None, description="روش پیشنهادی")
    is_public: bool = Field(default=False, description="عمومی بودن قالب")


class DecisionTemplateCreate(DecisionTemplateBase):
    """اسکیمای ایجاد قالب جدید"""
    pass


class DecisionTemplateUpdate(BaseModel):
    """اسکیمای به‌روزرسانی قالب"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    domain: Optional[str] = Field(None, max_length=100)
    default_criteria: Optional[List[Dict[str, Any]]] = None
    recommended_method: Optional[MCDMMethod] = None
    is_public: Optional[bool] = None


class DecisionTemplateResponse(DecisionTemplateBase):
    """اسکیمای پاسخ قالب"""
    id: int
    created_by: Optional[int] = None
    created_at: datetime


class DecisionTemplateListResponse(BaseSchema):
    """لیست قالب‌ها"""
    items: List[DecisionTemplateResponse]
    total: int


# ============================================================================
# Request/Response Wrappers
# ============================================================================

class AHPComparisonRequest(BaseModel):
    """درخواست مقایسه زوجی برای AHP"""
    criteria_ids: List[int] = Field(..., min_length=2, description="لیست معیارها برای مقایسه")
    comparisons: Dict[str, Dict[str, float]] = Field(
        ..., 
        description="مقایسات زوجی: {C1: {C2: 3.0, C3: 5.0}, ...}"
    )


class AHPWeightsResponse(BaseSchema):
    """پاسخ وزن‌های AHP"""
    weights: Dict[str, float] = Field(..., description="وزن هر معیار")
    consistency_ratio: float = Field(..., description="شاخص ناسازگاری")
    is_consistent: bool = Field(..., description="سازگار بودن ماتریس")
    eigenvalue: Optional[float] = Field(None, description="مقدار ویژه اصلی")


class TOPSISRequest(BaseModel):
    """درخواست تحلیل TOPSIS"""
    project_id: int
    normalize_method: str = Field(default="vector", description="روش نرمال‌سازی")
    distance_method: str = Field(default="euclidean", description="روش محاسبه فاصله")


class TOPSISResponse(BaseSchema):
    """پاسخ تحلیل TOPSIS"""
    positive_ideal_solution: Dict[str, float] = Field(..., description="راه‌حل ایده‌آل مثبت")
    negative_ideal_solution: Dict[str, float] = Field(..., description="راه‌حل ایده‌آل منفی")
    rankings: List[RankingItem] = Field(..., description="رتبه‌بندی گزینه‌ها")
    separation_measures: Dict[str, Dict[str, float]] = Field(
        ..., 
        description="فاصله از راه‌حل‌های ایده‌آل"
    )


class SensitivityAnalysisRequest(BaseModel):
    """درخواست تحلیل حساسیت"""
    analysis_id: int
    parameter: str = Field(..., description="پارامتر برای تغییر")
    variation_range: List[float] = Field(
        ..., 
        min_length=2,
        description="محدوده تغییرات پارامتر"
    )
    steps: int = Field(default=10, ge=2, le=100, description="تعداد گام‌ها")


class SensitivityAnalysisResponse(BaseSchema):
    """پاسخ تحلیل حساسیت"""
    original_ranking: List[RankingItem] = Field(..., description="رتبه‌بندی اصلی")
    sensitivity_results: List[Dict[str, Any]] = Field(
        ..., 
        description="نتایج برای هر گام تغییر"
    )
    stability_index: float = Field(..., description="شاخص پایداری رتبه‌بندی")
    critical_parameters: List[str] = Field(
        ..., 
        description="پارامترهای بحرانی که بیشترین تأثیر را دارند"
    )


# ============================================================================
# Statistics and Dashboard Schemas
# ============================================================================

class DecisionStatistics(BaseSchema):
    """آمار کلی سیستم تصمیم‌یار"""
    total_projects: int = 0
    active_projects: int = 0
    total_criteria: int = 0
    total_alternatives: int = 0
    total_analyses: int = 0
    methods_usage: Dict[str, int] = Field(default_factory=dict, description="تکرار استفاده از هر روش")
    recent_projects: List[DecisionProjectResponse] = Field(default_factory=list)


class CriterionGroupCreate(BaseModel):
    """ایجاد گروه معیار"""
    project_id: int
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    weight: Optional[float] = Field(None, ge=0, le=1)
    criterion_ids: List[int] = Field(default_factory=list, description="لیست معیارهای گروه")


class CriterionGroupResponse(BaseSchema):
    """پاسخ گروه معیار"""
    id: int
    project_id: int
    name: str
    description: Optional[str] = None
    weight: Optional[float] = None
    criteria_count: int = 0
    created_at: datetime
    criteria: List[DecisionCriterionResponse] = Field(default_factory=list)
