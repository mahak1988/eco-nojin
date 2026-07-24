# 📋 برنامه توسعه ماژول‌های دانش‌یار، تصمیم‌یار، آموزش‌یار و حسابداری

## 🎯 خلاصه اجرایی | Executive Summary

این سند برنامه توسعه چهار ماژول کلیدی پلتفرم EcoNojin را تشریح می‌کند:
- **دانش‌یار (Daneshyar/Knowledge Assistant)** - دستیار هوشمند پژوهش
- **تصمیم‌یار (DecisionYar/Decision Support)** - سیستم پشتیبانی تصمیم
- **آموزش‌یار (EducationYar/Education Assistant)** - پلتفرم آموزش
- **حسابداری و مالی (Accounting & Finance)** - مدیریت مالی و ECO

---

## ۱. 📊 وضعیت موجود | Current Status

### ۱.۱ دانش‌یار (Daneshyar)

| جنبه | وضعیت | توضیحات |
|------|--------|---------|
| **فرانت‌اند** | ✅ موجود | `/workspace/apps/web/src/pages/Daneshyar/Daneshyar.tsx` |
| **بک‌اند** | ⚠️ ناقص | `apps/shared_knowledge/` - فقط CRUD ساده |
| **API** | ❌ عدم وجود | هیچ endpoint تخصصی ندارد |
| **i18n** | ✅ کامل | تمام زبان‌ها در `fa.json` |
| **دیتابیس** | ⚠️ ساده | فقط جدول `shared_knowledge` |

**فایل‌های موجود:**
```
/workspace/apps/shared_knowledge/
├── models.py          # مدل SQLAlchemy ساده
├── schemas.py         # Pydantic schemas
├── service.py         # لایه سرویس
├── repository.py      # دسترسی به دیتابیس
├── router.py          # روتر FastAPI
└── knowledge/
    ├── models.py      # مدل‌های دانش
    ├── repository.py  # مخزن دانش
    └── seed_data.py   # داده‌های نمونه
```

### ۱.۲ تصمیم‌یار (DecisionYar)

| جنبه | وضعیت | توضیحات |
|------|--------|---------|
| **فرانت‌اند** | ✅ موجود | `/workspace/apps/web/src/pages/DecisionYar/DecisionYar.tsx` |
| **بک‌اند** | ❌ عدم وجود | هیچ ماژول اختصاصی ندارد |
| **API** | ❌ عدم وجود | هیچ endpoint ندارد |
| **i18n** | ✅ کامل | در `fa.json` تعریف شده |
| **هوش مصنوعی** | ⚠️ پراکنده | در `apps/ai_agents/agents/admin.py` |

### ۱.۳ آموزش‌یار (EducationYar)

| جنبه | وضعیت | توضیحات |
|------|--------|---------|
| **فرانت‌اند** | ❌ عدم وجود | هیچ صفحه‌ای ندارد |
| **بک‌اند** | ❌ عدم وجود | هیچ ماژولی ندارد |
| **API** | ❌ عدم وجود | هیچ endpoint ندارد |
| **i18n** | ⚠️ частичی | فقط واژه‌های عمومی آموزش |
| **محتوا** | ✅ موجود | در `/workspace/knowledge_hub/training_materials/` |

### ۱.۴ حسابداری و مالی (Accounting & Finance)

| جنبه | وضعیت | توضیحات |
|------|--------|---------|
| **فرانت‌اند** | ✅ کامل | `/workspace/apps/web/src/app/accounting/` |
| **بک‌اند** | ⚠️ ناقص | `apps/api/routes/accounting.py` - فقط mock data |
| **API** | ✅ موجود | ۱۰ endpoint تعریف شده |
| **دیتابیس** | ❌ عدم وجود | داده‌های sample در حافظه |
| **i18n** | ✅ کامل | تمام صفحات فارسی |

**فایل‌های موجود:**
```
/workspace/apps/web/src/app/accounting/
├── page.tsx           # داشبورد اصلی
├── transactions/
│   └── page.tsx       # صفحه تراکنش‌ها
└── invoices/
    └── page.tsx       # صفحه فاکتورها

/workspace/apps/api/routes/accounting.py
├── GET /transactions
├── GET /transactions/{id}
├── POST /transactions
├── GET /summary
├── GET /charts/*
├── GET /invoices
└── POST /upload/statement
```

---

## ۲. 🏗️ معماری پیشنهادی | Proposed Architecture

### ۲.۱ ساختار ماژول‌های بک‌اند

```
apps/
├── decision_support/          # تصمیم‌یار
│   ├── __init__.py
│   ├── router.py              # API endpoints
│   ├── schemas.py             # Pydantic models
│   ├── service.py             # Business logic
│   ├── models.py              # SQLAlchemy ORM
│   ├── repository.py          # DB access
│   ├── engines/               # موتورهای تصمیم‌گیری
│   │   ├── mcdm.py            # MCDM algorithms
│   │   ├── cost_benefit.py    # CBA analysis
│   │   └── lca.py             # Life Cycle Assessment
│   └── reports/               # تولید گزارش
│       └── generator.py
│
├── education/                 # آموزش‌یار
│   ├── __init__.py
│   ├── router.py
│   ├── schemas.py
│   ├── service.py
│   ├── models.py
│   ├── repository.py
│   ├── courses/               # مدیریت دوره‌ها
│   │   ├── models.py
│   │   └── service.py
│   ├── progress/              # پیگیری پیشرفت
│   │   └── tracker.py
│   └── assessments/           # ارزیابی‌ها
│       └── quiz_engine.py
│
├── knowledge_graph/           # دانش‌یار (توسعه یافته)
│   ├── __init__.py
│   ├── router.py
│   ├── schemas.py
│   ├── service.py
│   ├── models.py              # گراف دانش
│   ├── repository.py
│   ├── rag/                   # Retrieval Augmented Generation
│   │   ├── vector_store.py
│   │   └── semantic_search.py
│   └── analytics/             # تحلیل دانش
│       └── insights.py
│
└── accounting/                # حسابداری (توسعه یافته)
    ├── __init__.py
    ├── router.py              # جایگزین routes/accounting.py
    ├── schemas.py
    ├── service.py
    ├── models.py              # جداول حسابداری
    ├── repository.py
    ├── ledger/                # دفتر کل
    │   └── double_entry.py
    ├── reporting/             # گزارش‌گیری مالی
    │   ├── balance_sheet.py
    │   └── income_statement.py
    └── eco_token/             # مدیریت توکن ECO
        └── wallet.py
```

### ۲.۲ ساختار فرانت‌اند

```
apps/web/src/
├── app/
│   ├── decision/              # تصمیم‌یار
│   │   ├── page.tsx
│   │   ├── scenarios/
│   │   ├── analysis/
│   │   └── reports/
│   ├── education/             # آموزش‌یار
│   │   ├── page.tsx
│   │   ├── courses/
│   │   ├── my-learning/
│   │   └── assessments/
│   ├── knowledge/             # دانش‌یار
│   │   ├── page.tsx
│   │   ├── search/
│   │   ├── projects/
│   │   └── publications/
│   └── accounting/            # حسابداری (موجود - تکمیل شود)
│       ├── page.tsx
│       ├── transactions/
│       ├── invoices/
│       ├── reports/
│       └── wallet/
│
├── services/
│   ├── decisionService.ts
│   ├── educationService.ts
│   ├── knowledgeService.ts
│   └── accountingService.ts   # توسعه یابد
│
└── types/
    ├── decision.ts
    ├── education.ts
    ├── knowledge.ts
    └── accounting.ts          # توسعه یابد
```

---

## ۳. 📝 برنامه توسعه تفصیلی | Detailed Development Plan

### فاز ۱: زیرساخت و مدل‌های داده (هفته ۱-۲)

#### ۳.۱.۱ تصمیم‌یار - بک‌اند

**فایل‌های جدید:**

```python
# apps/decision_support/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship

class DecisionScenario(Base):
    __tablename__ = "decision_scenarios"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    criteria = Column(JSON)  # معیارهای تصمیم‌گیری
    alternatives = Column(JSON)  # گزینه‌های ممکن
    weights = Column(JSON)  # وزن معیارها
    result = Column(JSON)  # نتیجه تحلیل
    created_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"))

class MCDMResult(Base):
    __tablename__ = "mcdm_results"
    
    id = Column(Integer, primary_key=True)
    scenario_id = Column(Integer, ForeignKey("decision_scenarios.id"))
    method = Column(String(50))  # AHP, TOPSIS, ELECTRE
    ranking = Column(JSON)
    sensitivity = Column(JSON)
```

```python
# apps/decision_support/schemas.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class Criterion(BaseModel):
    name: str
    weight: float
    direction: str  # "maximize" or "minimize"

class Alternative(BaseModel):
    name: str
    scores: Dict[str, float]

class ScenarioCreate(BaseModel):
    name: str
    description: Optional[str] = None
    criteria: List[Criterion]
    alternatives: List[Alternative]

class ScenarioResponse(BaseModel):
    id: int
    name: str
    result: Optional[Dict[str, Any]]
    created_at: datetime
```

```python
# apps/decision_support/engines/mcdm.py
import numpy as np
from typing import List, Dict

class MCDMEngine:
    """موتور تصمیم‌گیری چندمعیاره"""
    
    @staticmethod
    def ahp(criteria_weights: Dict, comparison_matrix: List[List[float]]) -> Dict:
        """تحلیل سلسله مراتبی تحلیلی"""
        # پیاده‌سازی AHP
        pass
    
    @staticmethod
    def topsis(scores: np.ndarray, weights: np.ndarray) -> np.ndarray:
        """تکنیک TOPSIS برای رتبه‌بندی"""
        # پیاده‌سازی TOPSIS
        pass
```

```python
# apps/decision_support/router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/decision", tags=["decision-support"])

@router.post("/scenarios")
async def create_scenario(scenario: ScenarioCreate, db: AsyncSession = Depends(get_db)):
    """ایجاد سناریوی تصمیم‌گیری جدید"""
    pass

@router.post("/analyze/ahp")
async def analyze_ahp(scenario_id: int, db: AsyncSession = Depends(get_db)):
    """تحلیل با روش AHP"""
    pass

@router.get("/reports/{scenario_id}")
async def get_report(scenario_id: int, db: AsyncSession = Depends(get_db)):
    """دریافت گزارش تصمیم"""
    pass
```

#### ۳.۱.۲ آموزش‌یار - بک‌اند

```python
# apps/education/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    instructor_id = Column(Integer, ForeignKey("users.id"))
    duration_hours = Column(Float)
    level = Column(String(50))  # beginner, intermediate, advanced
    is_published = Column(Boolean, default=False)
    modules = relationship("CourseModule", back_populates="course")

class CourseModule(Base):
    __tablename__ = "course_modules"
    
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String(255))
    content = Column(Text)
    order = Column(Integer)
    video_url = Column(String(500))
    resources = Column(JSON)

class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    module_id = Column(Integer, ForeignKey("course_modules.id"))
    completed = Column(Boolean, default=False)
    score = Column(Float)
    completed_at = Column(DateTime)
```

```python
# apps/education/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ModuleCreate(BaseModel):
    title: str
    content: str
    order: int
    video_url: Optional[str] = None

class CourseCreate(BaseModel):
    title: str
    description: str
    duration_hours: float
    level: str
    modules: List[ModuleCreate]

class ProgressUpdate(BaseModel):
    module_id: int
    completed: bool
    score: Optional[float] = None
```

```python
# apps/education/router.py
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api/v1/education", tags=["education"])

@router.get("/courses")
async def list_courses(level: Optional[str] = None):
    """فهرست دوره‌ها"""
    pass

@router.post("/courses")
async def create_course(course: CourseCreate):
    """ایجاد دوره جدید"""
    pass

@router.get("/my-progress")
async def get_user_progress(user_id: int):
    """پیشرفت کاربر"""
    pass

@router.post("/progress")
async def update_progress(progress: ProgressUpdate):
    """به‌روزرسانی پیشرفت"""
    pass
```

#### ۳.۱.۳ دانش‌یار - توسعه بک‌اند

```python
# apps/knowledge_graph/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship

class KnowledgeNode(Base):
    """گره‌های گراف دانش"""
    __tablename__ = "knowledge_nodes"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    node_type = Column(String(50))  # concept, paper, dataset, tool
    metadata = Column(JSON)
    embeddings = Column(JSON)  # بردارهای تعبیه‌شده
    created_at = Column(DateTime)

class KnowledgeRelation(Base):
    """روابط بین گره‌های دانش"""
    __tablename__ = "knowledge_relations"
    
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("knowledge_nodes.id"))
    target_id = Column(Integer, ForeignKey("knowledge_nodes.id"))
    relation_type = Column(String(50))  # related_to, extends, contradicts
    confidence = Column(Float)
```

```python
# apps/knowledge_graph/rag/semantic_search.py
from typing import List, Dict
from sentence_transformers import SentenceTransformer

class SemanticSearch:
    """جستجوی معنایی در گراف دانش"""
    
    def __init__(self):
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    async def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """جستجوی معنایی"""
        query_embedding = self.model.encode(query)
        # جستجو در vector store
        return results
    
    async def suggest_related(self, node_id: int) -> List[Dict]:
        """پیشنهاد گره‌های مرتبط"""
        pass
```

#### ۳.۱.۴ حسابداری - تکمیل بک‌اند

```python
# apps/accounting/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

class TransactionType(enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    ECO_REWARD = "eco_reward"
    CARBON_CREDIT = "carbon_credit"

class Account(Base):
    """جدول حساب‌ها"""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    account_type = Column(String(50))  # asset, liability, equity, income, expense
    parent_id = Column(Integer, ForeignKey("accounts.id"))
    balance = Column(Float, default=0)
    currency = Column(String(3), default="USD")

class Transaction(Base):
    """جدول تراکنش‌ها"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    type = Column(Enum(TransactionType))
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    description = Column(Text)
    category = Column(String(100))
    account_id = Column(Integer, ForeignKey("accounts.id"))
    reference_id = Column(String(100))  # شماره مرجع
    status = Column(String(50), default="pending")  # pending, confirmed, cancelled
    transaction_date = Column(DateTime)
    created_at = Column(DateTime)

class Invoice(Base):
    """جدول فاکتورها"""
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True)
    invoice_number = Column(String(50), unique=True)
    client_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float, nullable=False)
    tax = Column(Float, default=0)
    total = Column(Float)
    status = Column(String(50), default="draft")
    issue_date = Column(DateTime)
    due_date = Column(DateTime)
```

```python
# apps/accounting/ledger/double_entry.py
from typing import Tuple, List

class DoubleEntryLedger:
    """سیستم دفترداری دوطرفه"""
    
    async def record_transaction(self, debit_account: int, credit_account: int, 
                                  amount: float, description: str):
        """ثبت تراکنش دوطرفه"""
        # بررسی توازن
        # ثبت در دفتر کل
        pass
    
    async def get_balance_sheet(self, date: datetime) -> Dict:
        """ترازنامه"""
        pass
    
    async def get_income_statement(self, start_date: datetime, end_date: datetime) -> Dict:
        """صورت سود و زیان"""
        pass
```

### فاز ۲: API و یکپارچه‌سازی (هفته ۳-۴)

#### ۳.۲.۱ ثبت روترها در main.py

```python
# apps/main.py
from fastapi import FastAPI
from apps.decision_support.router import router as decision_router
from apps.education.router import router as education_router
from apps.knowledge_graph.router import router as knowledge_router
from apps.accounting.router import router as accounting_router

app = FastAPI(title="EcoNojin API")

app.include_router(decision_router)
app.include_router(education_router)
app.include_router(knowledge_router)
app.include_router(accounting_router)
```

#### ۳.۲.۲ سرویس‌های فرانت‌اند

```typescript
// apps/web/src/services/decisionService.ts
import api from './apiClient';
import type { Scenario, AnalysisResult } from '@/types/decision';

export const decisionService = {
  async createScenario(scenario: Partial<Scenario>): Promise<Scenario> {
    const response = await api.post('/api/v1/decision/scenarios', scenario);
    return response.data;
  },
  
  async analyzeAHP(scenarioId: number): Promise<AnalysisResult> {
    const response = await api.post(`/api/v1/decision/analyze/ahp`, { scenario_id: scenarioId });
    return response.data;
  },
  
  async getReport(scenarioId: number): Promise<any> {
    const response = await api.get(`/api/v1/decision/reports/${scenarioId}`);
    return response.data;
  }
};
```

```typescript
// apps/web/src/services/educationService.ts
import api from './apiClient';
import type { Course, Progress } from '@/types/education';

export const educationService = {
  async listCourses(level?: string): Promise<Course[]> {
    const params = level ? { level } : {};
    const response = await api.get('/api/v1/education/courses', { params });
    return response.data;
  },
  
  async getMyProgress(): Promise<Progress[]> {
    const response = await api.get('/api/v1/education/my-progress');
    return response.data;
  },
  
  async updateProgress(moduleId: number, completed: boolean, score?: number): Promise<Progress> {
    const response = await api.post('/api/v1/education/progress', {
      module_id: moduleId,
      completed,
      score
    });
    return response.data;
  }
};
```

### فاز ۳: صفحات فرانت‌اند (هفته ۵-۶)

#### ۳.۳.۱ صفحه تصمیم‌یار

```tsx
// apps/web/src/app/decision/page.tsx
'use client';
import { useState, useEffect } from 'react';
import { decisionService } from '@/services/decisionService';
import { PageHeader } from '@/components/shared/PageHeader';
import { Target } from 'lucide-react';

export default function DecisionDashboard() {
  const [scenarios, setScenarios] = useState([]);
  
  useEffect(() => {
    // بارگذاری سناریوها
  }, []);
  
  return (
    <div className='container mx-auto px-4 py-8'>
      <PageHeader title='تصمیم‌یار' description='سیستم پشتیبانی تصمیم محیط‌زیستی' icon={Target} />
      {/* محتوای صفحه */}
    </div>
  );
}
```

#### ۳.۳.۲ صفحه آموزش‌یار

```tsx
// apps/web/src/app/education/page.tsx
'use client';
import { educationService } from '@/services/educationService';
import { BookOpen } from 'lucide-react';

export default function EducationDashboard() {
  const [courses, setCourses] = useState([]);
  const [progress, setProgress] = useState([]);
  
  return (
    <div className='container mx-auto px-4 py-8'>
      <PageHeader title='آموزش‌یار' description='پلتفرم آموزش کشاورزی پایدار' icon={BookOpen} />
      {/* فهرست دوره‌ها و پیشرفت */}
    </div>
  );
}
```

### فاز ۴: تست و مستندات (هفته ۷-۸)

- نوشتن تست‌های واحد برای هر ماژول
- تست یکپارچگی API
- مستندات Swagger/OpenAPI
- راهنمای کاربر فارسی/انگلیسی

---

## ۴. 📅 زمان‌بندی | Timeline

| فاز | فعالیت | مدت | خروجی |
|-----|---------|-----|--------|
| **فاز ۱** | مدل‌های داده و زیرساخت | ۲ هفته | ۴ ماژول بک‌اند با CRUD کامل |
| **فاز ۲** | API و منطق کسب‌وکار | ۲ هفته | APIهای تخصصی + سرویس‌های فرانت |
| **فاز ۳** | صفحات فرانت‌اند | ۲ هفته | ۱۲ صفحه جدید |
| **فاز ۴** | تست و مستندات | ۲ هفته | تست‌ها + مستندات کامل |
| **جمع** | | **۸ هفته** | **۴ ماژول کامل** |

---

## ۵. 🔧 وابستگی‌های فنی | Technical Dependencies

### بک‌اند (Python)
```toml
# pyproject.toml
[tool.poetry.dependencies]
fastapi = "^0.109.0"
sqlalchemy = "^2.0.0"
pydantic = "^2.5.0"
numpy = "^1.26.0"
scipy = "^1.12.0"  # برای محاسبات MCDM
sentence-transformers = "^2.3.0"  # برای جستجوی معنایی
chromadb = "^0.4.0"  # vector store
alembic = "^1.13.0"  # migrations
```

### فرانت‌اند (TypeScript)
```json
// package.json
{
  "dependencies": {
    "recharts": "^2.10.0",
    "framer-motion": "^11.0.0",
    "lucide-react": "^0.300.0",
    "@tanstack/react-query": "^5.0.0"
  }
}
```

---

## ۶. ✅ معیارهای پذیرش | Acceptance Criteria

### دانش‌یار
- [ ] جستجوی معنایی با دقت > 85%
- [ ] پیشنهاد گره‌های مرتبط
- [ ] تولید گزارش خودکار
- [ ] پشتیبانی از فارسی/انگلیسی

### تصمیم‌یار
- [ ] پیاده‌سازی AHP و TOPSIS
- [ ] تحلیل حساسیت
- [ ] تولید گزارش تصمیم
- [ ] ذخیره سناریوها

### آموزش‌یار
- [ ] مدیریت دوره‌ها و ماژول‌ها
- [ ] پیگیری پیشرفت کاربر
- [ ] سیستم ارزیابی و آزمون
- [ ] گواهینامه پایان دوره

### حسابداری
- [ ] دفترداری دوطرفه کامل
- [ ] گزارش‌های مالی استاندارد
- [ ] مدیریت توکن ECO
- [ ] صادرات گزارش‌ها (PDF, Excel)

---

## ۷. 📞 تیم توسعه | Development Team

| نقش | مسئولیت |
|-----|---------|
| Backend Lead | طراحی مدل‌ها و APIها |
| Frontend Lead | صفحات و سرویس‌ها |
| AI Engineer | موتورهای MCDM و RAG |
| QA Engineer | تست و اعتبارسنجی |
| DevOps | استقرار و CI/CD |

---

## ۸. 🚀 گام بعدی | Next Steps

1. **تأیید برنامه** توسط ذینفعان
2. **ایجاد branchهای توسعه** برای هر ماژول
3. **شروع فاز ۱** - مدل‌های داده
4. **بررسی هفتگی** پیشرفت

---

**تهیه‌شده توسط:** تیم توسعه EcoNojin  
**تاریخ:** ۲۰۲۵-۰۷-۲۴  
**نسخه:** 1.0
