# simulation | ماژول شبیه‌سازی جامع Econojin

> **نکته:** این ماژول **هسته شبیه‌سازی** پلتفرم Econojin است.
> شامل ۲۸+ شبیه‌ساز تخصصی در حوزه‌های اقلیم، کشاورزی، اقتصاد، انرژی، آب، خاک،
> تنوع زیستی، کربن، و خدمات اکوسیستمی.

## مسئولیت‌ها

این ماژول شش وظیفه‌ی اصلی دارد:

1. **۲۸+ شبیه‌ساز تخصصی** — مدل‌سازی حوزه‌های مختلف محیط زیستی و اقتصادی
2. **ثبت و مدیریت شبیه‌سازها** (`registry.py`) — ثبت خودکار شبیه‌سازها با دکوراتور
3. **زنجیره شبیه‌سازی** (`chain/`) — اجرای زنجیره‌ای شبیه‌سازها با خروجی→ورودی
4. **گزارش‌گیری** (`reports/`) — تولید گزارش CSV/JSON از نتایج شبیه‌سازی
5. **اعتبارسنجی** (`validation/`) — اعتبارسنجی داده‌های ورودی و خروجی
6. **API شبیه‌سازی** (`router.py`) — اجرا، پایش و مدیریت شبیه‌سازی‌ها

## ساختار

```
simulation/
├── __init__.py                # Module init
├── base.py                    # ★ کلاس پایه Simulator
├── registry.py                # ★ ثبت خودکار شبیه‌سازها
├── router.py                  # ★ FastAPI router
├── schemas.py                 # Pydantic validation models
├── service.py                 # Business logic
├── repository.py              # Database access
├── models.py                  # ORM models
├── dependencies.py            # FastAPI dependencies
│
├── climate/                   # ★ شبیه‌سازهای اقلیم
├── agriculture/               # ★ شبیه‌سازهای کشاورزی
├── economics/                 # ★ شبیه‌سازهای اقتصادی
├── energy/                    # ★ شبیه‌سازهای انرژی
├── hydrology/                 # ★ شبیه‌سازهای آب‌شناسی
├── soil/                      # ★ شبیه‌سازهای خاک
├── biodiversity/              # ★ شبیه‌سازهای تنوع زیستی
├── carbon_cycle/              # ★ شبیه‌سازهای چرخه کربن
├── ecosystem_services/        # ★ شبیه‌سازهای خدمات اکوسیستمی
├── water_quality/             # ★ شبیه‌سازهای کیفیت آب
├── urban/                     # ★ شبیه‌سازهای شهری
├── earth_engine/              # ★ شبیه‌سازهای مهندسی زمین
│
├── chain/                     # ★ زنجیره شبیه‌سازی
│   ├── router.py              #   API زنجیره
│   └── ...
├── reports/                   # ★ گزارش‌گیری
│   ├── router.py              #   API گزارش
│   └── ...
├── validation/                # ★ اعتبارسنجی
├── data/                      # ★ داده‌های شبیه‌سازی
├── runs/                      # ★ نتایج اجراها
├── advisory/                  # ★ مشاوره هوشمند
└── tests/                     # Pytest tests
```

## کلاس پایه Simulator (`base.py`)

تمامی شبیه‌سازها از کلاس پایه `Simulator` ارث می‌برند:

```python
from simulation.base import Simulator

class MySimulator(Simulator):
    """شبیه‌ساز سفارشی"""
    
    name = "my_simulator"
    description = "توضیحات شبیه‌ساز"
    inputs = [{"name": "param1", "type": "float", "description": "..."}]
    outputs = [{"name": "result1", "type": "float", "description": "..."}]
    
    async def run(self, inputs: dict) -> dict:
        # منطق شبیه‌سازی
        return {"result1": 42.0}
```

## ثبت خودکار شبیه‌سازها (`registry.py`)

شبیه‌سازها با دکوراتور `@register_simulator` به صورت خودکار ثبت می‌شوند:

```python
from simulation.registry import register_simulator

@register_simulator
class ClimateModel(Simulator):
    name = "climate_model"
    ...
```

## ۲۸+ شبیه‌ساز تخصصی

### 🌤️ اقلیم (Climate)
| شبیه‌ساز | توضیح |
|----------|--------|
| `climate_model` | مدل‌سازی تغییرات اقلیمی |
| `weather_generator` | تولید داده‌های هواشناسی |
| `precipitation` | شبیه‌سازی بارش |
| `temperature` | شبیه‌سازی دما |

### 🌾 کشاورزی (Agriculture)
| شبیه‌ساز | توضیح |
|----------|--------|
| `crop_growth` | رشد محصولات کشاورزی |
| `irrigation` | مدیریت آبیاری |
| `yield_prediction` | پیش‌بینی عملکرد محصول |
| `pest_dynamics` | پویایی آفات |

### 💰 اقتصاد (Economics)
| شبیه‌ساز | توضیح |
|----------|--------|
| `market_model` | مدل بازار و قیمت‌ها |
| `supply_chain` | زنجیره تأمین |
| `cost_benefit` | تحلیل هزینه-فایده |

### ⚡ انرژی (Energy)
| شبیه‌ساز | توضیح |
|----------|--------|
| `renewable_potential` | پتانسیل انرژی تجدیدپذیر |
| `energy_demand` | پیش‌بینی تقاضای انرژی |
| `grid_optimization` | بهینه‌سازی شبکه برق |

### 💧 آب (Hydrology)
| شبیه‌ساز | توضیح |
|----------|--------|
| `watershed_model` | مدل حوضه آبریز |
| `groundwater` | شبیه‌سازی آب زیرزمینی |
| `reservoir` | مدیریت مخازن |

### 🌱 خاک (Soil)
| شبیه‌ساز | توضیح |
|----------|--------|
| `soil_carbon` | کربن آلی خاک |
| `erosion` | فرسایش خاک |
| `nutrient_cycle` | چرخه مواد مغذی |

### 🦋 تنوع زیستی (Biodiversity)
| شبیه‌ساز | توضیح |
|----------|--------|
| `species_distribution` | پراکنش گونه‌ها |
| `habitat_suitability` | suitability زیستگاه |
| `population_dynamics` | پویایی جمعیت |

### 🌍 چرخه کربن (Carbon Cycle)
| شبیه‌ساز | توضیح |
|----------|--------|
| `carbon_flux` | شار کربن |
| `sequestration` | ترسیب کربن |
| `emissions` | انتشار گازهای گلخانه‌ای |

### 🏙️ شهری (Urban)
| شبیه‌ساز | توضیح |
|----------|--------|
| `urban_heat` | جزیره حرارتی شهری |
| `land_use` | تغییر کاربری زمین |
| `green_infrastructure` | زیرساخت سبز |

## Endpointهای API

### شبیه‌سازی

| Method | Path | توضیح |
|--------|------|--------|
| POST | `/api/v1/simulation/run` | اجرای شبیه‌سازی |
| GET | `/api/v1/simulation/runs` | لیست اجراهای قبلی |
| GET | `/api/v1/simulation/runs/{id}` | جزئیات یک اجرا |
| GET | `/api/v1/simulation/simulators` | لیست شبیه‌سازهای موجود |

**اجرای شبیه‌سازی:**
```json
// POST /api/v1/simulation/run
{
    "simulator": "climate_model",
    "inputs": {
        "temperature": 1.5,
        "precipitation": -10,
        "years": 50
    },
    "chain": ["climate_model", "crop_growth", "market_model"]
}
```

### زنجیره شبیه‌سازی (Chain)

| Method | Path | توضیح |
|--------|------|--------|
| POST | `/api/v1/simulation/chain/run` | اجرای زنجیره شبیه‌سازها |
| GET | `/api/v1/simulation/chain/chains` | لیست زنجیره‌های تعریف‌شده |

### گزارش‌گیری (Reports)

| Method | Path | توضیح |
|--------|------|--------|
| GET | `/api/v1/simulation/reports/csv` | خروجی CSV |
| GET | `/api/v1/simulation/reports/json` | خروجی JSON |

## توسعه و تست

```bash
# از ریشه‌ی پروژه
cd d:\econojin.com

# اجرای تست‌ها
pytest apps/simulation/tests/ -v

# تست یک شبیه‌ساز خاص
pytest apps/simulation/tests/test_climate.py -v

# اجرای سرور توسعه
python apps/main.py
# یا
uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000
```

## تغییرات مهم

- **فاز ۲:** بازنویسی کامل با معماری شبیه‌ساز پایه (`base.py`)
- **فاز ۲:** افزودن ۲۸+ شبیه‌ساز تخصصی در ۱۱ حوزه
- **فاز ۲:** سیستم ثبت خودکار با دکوراتور (`registry.py`)
- **فاز ۲:** زنجیره شبیه‌سازی (خروجی یک شبیه‌ساز → ورودی شبیه‌ساز بعدی)
- **فاز ۲:** گزارش‌گیری CSV/JSON
- **فاز ۲:** اعتبارسنجی ورودی و خروجی
