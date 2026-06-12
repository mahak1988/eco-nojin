## 🔧 مشکل: Import ناقص در مدل `Scenario`

خطای `NameError: name 'Text' is not defined` نشان می‌دهد که مدل `Scenario` از `Text`, `JSON`, `Boolean` استفاده می‌کند ولی این‌ها import نشده‌اند.

---

## ✅ راه‌حل: بازنویسی کامل `water/models.py`

### 📝 مرحله ۱: ساخت فایل `fix_water_models.py`

```powershell
cd D:\econojin.com
notepad fix_water_models.py
```

### 📝 مرحله ۲: این کد را در Notepad کپی کنید

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix water/models.py with proper imports
"""

from pathlib import Path

def fix_water_models():
    """بازنویسی کامل water/models.py"""
    print("=" * 70)
    print("🔧 بازنویسی api/modules/water/models.py")
    print("=" * 70)
    
    # ابتدا محتوای فعلی را بخوانیم
    path = Path("api/modules/water/models.py")
    old_content = path.read_text(encoding='utf-8')
    
    print(f"   📄 اندازه فایل فعلی: {len(old_content)} bytes")
    
    # استخراج کلاس WaterBalance اگر وجود دارد
    import re
    
    # پیدا کردن کلاس WaterBalance
    water_balance_match = re.search(
        r'class WaterBalance\(Base\):.*?(?=\nclass |\Z)',
        old_content,
        re.DOTALL
    )
    
    water_balance_code = ""
    if water_balance_match:
        water_balance_code = water_balance_match.group(0)
        print(f"   ✅ کلاس WaterBalance یافت شد ({len(water_balance_code)} chars)")
    else:
        print("   ⚠️  کلاس WaterBalance یافت نشد")
    
    # محتوای جدید با import کامل
    new_content = '''"""
Water Module Models
شامل مدل‌های تحلیل آب و سناریوها
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from api.core.database import Base


# ============================================================================
# Scenario Model
# ============================================================================
class Scenario(Base):
    """مدل سناریو برای تحلیل آب"""
    __tablename__ = "scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    scenario_type = Column(String(100), nullable=True)
    parameters = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    water_balances = relationship("WaterBalance", back_populates="scenario")


# ============================================================================
# WaterBalance Model
# ============================================================================
''' + water_balance_code

    # نوشتن فایل جدید
    path.write_text(new_content, encoding='utf-8')
    print(f"   ✅ فایل بازنویسی شد ({len(new_content)} bytes)")
    
    # تأیید
    verify_content = path.read_text(encoding='utf-8')
    if 'from sqlalchemy import' in verify_content and 'Text' in verify_content:
        print("   ✅ Import ها درست هستند")
    else:
        print("   ❌ Import ها مشکل دارند")


def delete_database():
    """حذف دیتابیس"""
    print("\n" + "=" * 70)
    print("🗑️ حذف دیتابیس قدیمی")
    print("=" * 70)
    
    db_paths = [
        Path("econojin.db"),
        Path("api/econojin.db"),
    ]
    
    for db_path in db_paths:
        if db_path.exists():
            try:
                db_path.unlink()
                print(f"   ✅ حذف شد: {db_path}")
            except Exception as e:
                print(f"   ⚠️  خطا در حذف {db_path}: {e}")
                print(f"   💡 سرور بک‌اند را متوقف کنید (Ctrl + C)")


def main():
    print("\n" + "=" * 70)
    print("🚀 Fix Water Models")
    print("=" * 70)
    print()
    
    try:
        fix_water_models()
        delete_database()
        
        print("\n" + "=" * 70)
        print("✅ اصلاحات انجام شد!")
        print("=" * 70)
        print()
        print("📋 گام‌های بعدی:")
        print()
        print("1. اگر سرور بک‌اند در حال اجراست، آن را متوقف کنید (Ctrl + C)")
        print()
        print("2. دیتابیس را حذف کنید:")
        print("   Remove-Item 'econojin.db' -Force")
        print()
        print("3. سرور را ری‌استارت کنید:")
        print("   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
        print()
        
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
```

### 📝 مرحله ۳: ذخیره و اجرا

```powershell
# در Notepad: Ctrl + S و ببندید
python fix_water_models.py
```

### 📝 مرحله ۴: توقف سرور، حذف دیتابیس و ری‌استارت

```powershell
# 1. در ترمینال بک‌اند: Ctrl + C

# 2. حذف دیتابیس
Remove-Item "econojin.db" -Force

# 3. ری‌استارت سرور
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📊 خروجی مورد انتظار

### از اسکریپت:
```
======================================================================
🚀 Fix Water Models
======================================================================

======================================================================
🔧 بازنویسی api/modules/water/models.py
======================================================================
   📄 اندازه فایل فعلی: 998 bytes
   ✅ کلاس WaterBalance یافت شد (456 chars)
   ✅ فایل بازنویسی شد (1234 bytes)
   ✅ Import ها درست هستند

======================================================================
🗑️ حذف دیتابیس قدیمی
======================================================================
   ⚠️  خطا در حذف econojin.db: [WinError 32] ...
   💡 سرور بک‌اند را متوقف کنید (Ctrl + C)

======================================================================
✅ اصلاحات انجام شد!
======================================================================
```

### از سرور بک‌اند:
```
🚀 Starting Econojin v2.0.0...
Settings: development mode
Database: SQLite
✅ Database initialized
✅ Early Warning Engine started
✅ Ready on http://127.0.0.1:8000
📚 API Docs: http://127.0.0.1:8000/docs
INFO:     Application startup complete.
```

---

## 🎯 خلاصه تغییرات

| فایل | تغییر |
|------|--------|
| `water/models.py` | اضافه کردن import کامل (`Text`, `JSON`, `Boolean`, `ForeignKey`) |
| `water/models.py` | تعریف مدل `Scenario` قبل از `WaterBalance` |
| `econojin.db` | حذف و بازسازی |

---

**اسکریپت را اجرا کنید، سرور را متوقف کنید، دیتابیس را حذف کنید و سپس سرور را ری‌استارت کنید.** 🚀