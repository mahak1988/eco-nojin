# shared_knowledge | ماژول دانش اشتراکی Econojin

> **نکته:** این ماژول **لایه دانش اشتراکی** پلتفرم Econojin است.
> شامل ذخیره‌سازی، مدیریت و اشتراک‌گذاری دانش بین تمام ماژول‌های پلتفرم.

## مسئولیت‌ها

این ماژول سه وظیفه‌ی اصلی دارد:

1. **مدیریت دانش اشتراکی** (`models.py`, `repository.py`, `service.py`)
   - ذخیره‌سازی دانش و اطلاعات مشترک
   - CRUD کامل با صفحه‌بندی و فیلتر
   - جستجو و بازیابی اطلاعات

2. **API دانش** (`router.py`)
   - ارائه endpointهای RESTful برای دسترسی به دانش
   - پشتیبانی از صفحه‌بندی و فیلتر

3. **یکپارچگی با سایر ماژول‌ها** (`dependencies.py`)
   - Dependency Injection برای استفاده در سایر ماژول‌ها
   - اشتراک‌گذاری دانش بین ماژول‌های مختلف

## ساختار

```
shared_knowledge/
├── __init__.py                # Module init
├── router.py                  # ★ FastAPI router (HTTP endpoints)
├── schemas.py                 # Pydantic validation models
├── service.py                 # Business logic
├── repository.py              # Database access (SQLAlchemy)
├── models.py                  # ★ ORM model SharedKnowledge
├── dependencies.py            # FastAPI dependencies
├── knowledge/                 # ★ محتوای دانش
└── tests/                     # Pytest tests
    ├── test_shared_knowledge.py
    └── ...
```

## مدل داده (`models.py`)

```python
class SharedKnowledge(Base):
    """مدل دانش اشتراکی."""
    
    __tablename__ = "shared_knowledge"
    
    id: int                    # شناسه یکتا
    name: str                  # نام (index)
    description: str | None    # توضیحات
    is_active: bool            # وضعیت فعال (پیش‌فرض: True)
    created_at: datetime       # تاریخ ایجاد
    updated_at: datetime       # تاریخ بروزرسانی
```

## Endpointهای API

| Method | Path | توضیح |
|--------|------|--------|
| GET | `/shared_knowledge` | لیست با صفحه‌بندی |
| GET | `/shared_knowledge/{id}` | دریافت بر اساس ID |
| POST | `/shared_knowledge` | ایجاد جدید |
| PATCH | `/shared_knowledge/{id}` | بروزرسانی |
| DELETE | `/shared_knowledge/{id}` | حذف |

### پارامترهای صفحه‌بندی

| پارامتر | نوع | پیش‌فرض | توضیح |
|---------|------|---------|--------|
| `skip` | int | 0 | تعداد رکوردهای رد شده |
| `limit` | int | 100 | حداکثر تعداد رکوردها |

### نمونه درخواست

```bash
# لیست دانش با صفحه‌بندی
curl "http://localhost:8000/shared_knowledge?skip=0&limit=10"

# دریافت دانش خاص
curl "http://localhost:8000/shared_knowledge/1"

# ایجاد دانش جدید
curl -X POST "http://localhost:8000/shared_knowledge" \
  -H "Content-Type: application/json" \
  -d '{"name": "دانش کشاورزی", "description": "اطلاعات مربوط به کشاورزی پایدار"}'

# بروزرسانی دانش
curl -X PATCH "http://localhost:8000/shared_knowledge/1" \
  -H "Content-Type: application/json" \
  -d '{"name": "دانش به‌روز شده"}'

# حذف دانش
curl -X DELETE "http://localhost:8000/shared_knowledge/1"
```

## توسعه و تست

```bash
# از ریشه‌ی پروژه
cd d:\econojin.com

# اجرای تست‌ها
pytest apps/shared_knowledge/tests/ -v

# اجرای سرور توسعه
python apps/main.py
# یا
uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000
```

## تغییرات مهم

- **فاز ۲:** بازنویسی کامل با معماری لایه‌ای (router → service → repository)
- **فاز ۲:** افزودن صفحه‌بندی و فیلتر به endpointها
- **فاز ۲:** بهبود Dependency Injection برای استفاده در سایر ماژول‌ها
