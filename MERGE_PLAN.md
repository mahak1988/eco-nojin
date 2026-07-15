# 📋 نقشه ادغام DDD

تولید شده در: 2026-07-11 02:38:37

## 📊 آمار

- تعداد کل فایل‌ها: 490
- فایل‌های استفاده‌نشده: 189

## 🔄 برنامه انتقال

### apps/ai_agents/ → apps/api/app/domain/ai_agents/

- **دلیل**: ادغام در لایه domain
- **تعداد فایل‌ها**: 0

### apps/users/ → apps/api/app/domain/user/

- **دلیل**: ادغام با ساختار DDD موجود
- **تعداد فایل‌ها**: 0

### apps/shared/ai/ → apps/api/app/infrastructure/ai/

- **دلیل**: انتقال به infrastructure
- **تعداد فایل‌ها**: 0

### apps/shared/database/ → apps/api/app/infrastructure/database/

- **دلیل**: انتقال به infrastructure
- **تعداد فایل‌ها**: 0

### apps/shared/knowledge/ → apps/api/app/infrastructure/knowledge/

- **دلیل**: انتقال به infrastructure
- **تعداد فایل‌ها**: 0

### apps/simulation/ → apps/api/app/scientific/

- **دلیل**: ادغام با scientific wrappers
- **تعداد فایل‌ها**: 0

## 🗑️ فایل‌های حذف‌شدنی

- `apps\analyze_dependencies.py`
- `apps\analyze_project.py`
- `apps\api\run.py`
- `apps\simulation\water_quality\integration\pollutant_bridge.py`
- `apps\simulation\water_quality\integration\water_quality_orchestrator.py`
- `apps\simulation\water_quality\qual2k\wqi_calculator.py`
- `apps\simulation\water_quality\qual2k\wrapper.py`
- `apps\simulation\water_quality\wasp\eutrophication_model.py`
- `apps\simulation\water_quality\wasp\wrapper.py`
- `apps\simulation\soil\epic\soil_productivity.py`
- `apps\simulation\soil\epic\wrapper.py`
- `apps\simulation\soil\integration\soil_health_bridge.py`
- `apps\simulation\soil\integration\soil_orchestrator.py`
- `apps\simulation\soil\rusle2\erosion_factors.py`
- `apps\simulation\soil\rusle2\wrapper.py`
- `apps\simulation\hydrology\bridge\data_transformer.py`
- `apps\simulation\hydrology\bridge\orchestrator.py`
- `apps\simulation\hydrology\hecras\flood_analyzer.py`
- `apps\simulation\hydrology\hecras\wrapper.py`
- `apps\simulation\hydrology\integration\coupled_orchestrator.py`

## 🔧 به‌روزرسانی Imports

| الگوی قدیمی | الگوی جدید | تعداد |
|-------------|------------|-------|
| `from apps.ai_agents.` | `from apps.api.app.domain.ai_agents.` | 14 |
| `from apps.users.` | `from apps.api.app.domain.user.` | 14 |
| `from apps.shared.ai.` | `from apps.api.app.infrastructure.ai.` | 53 |
| `from apps.shared.database.` | `from apps.api.app.infrastructure.database.` | 25 |
| `from apps.shared.knowledge.` | `from apps.api.app.infrastructure.knowledge.` | 9 |
| `from apps.simulation.` | `from apps.api.app.scientific.` | 1 |
