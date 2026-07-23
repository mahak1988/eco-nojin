# shared_sim | ماژول شبیه‌سازی اشتراکی Econojin

> **نکته:** این ماژول **لایه شبیه‌سازی اشتراکی** پلتفرم Econojin است.
> شامل مدل‌ها، سرویس‌ها و ابزارهای مشترک برای تمام ماژول‌های شبیه‌سازی.

## مسئولیت‌ها

این ماژول سه وظیفه‌ی اصلی دارد:

1. **مدل‌های اشتراکی شبیه‌سازی** (`models.py`, `repository.py`, `service.py`)
   - ذخیره‌سازی داده‌های مشترک شبیه‌سازی
   - CRUD کامل با صفحه‌بندی و فیلتر

2. **API شبیه‌سازی اشتراکی** (`router.py`)
   - ارائه endpointهای RESTful برای دسترسی به داده‌های شبیه‌سازی
   - پشتیبانی از صفحه‌بندی

3. **یکپارچگی با ماژول‌های شبیه‌سازی** (`dependencies.py`)
   - Dependency Injection برای استفاده در `apps/simulation/`
   - اشتراک‌گذاری سرویس‌های شبیه‌سازی

## ساختار

```
shared_sim/
├── __init__.py                # Module init
├── router.py                  # ★ FastAPI router (HTTP endpoints)
├── schemas.py                 # Pydantic validation models
├── service.py                 # Business logic
├── repository.py              # Database access (SQLAlchemy)
├── models.py                  # ★ ORM model SharedSim
├── dependencies.py            # FastAPI dependencies
└── tests/                     # Pytest tests
    ├── test_shared_sim.py
    └── ...
```

## مدل داده (`models.py`)

```python
class SharedSim(Base):
    """مدل اشتراکی شبیه‌سازی."""
    
    __tablename__ = "shared_sim"
    
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
| GET | `/shared_sim` | لیست با صفحه‌بندی |
| GET | `/shared_sim/{id}` | دریافت بر اساس ID |
| POST | `/shared_sim` | ایجاد جدید |
| PATCH | `/shared_sim/{id}` | بروزرسانی |
| DELETE | `/shared_sim/{id}` | حذف |

## توسعه و تست

```bash
# از ریشه‌ی پروژه
cd d:\econojin.com

# اجرای تست‌ها
pytest apps/shared_sim/tests/ -v

# اجرای سرور توسعه
python apps/main.py
# یا
uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000
```

## تغییرات مهم

- **فاز ۲:** بازنویسی کامل با معماری لایه‌ای (router → service → repository)
- **فاز ۲:** افزودن صفحه‌بندی به endpointها
- **فاز ۲:** بهبود Dependency Injection
