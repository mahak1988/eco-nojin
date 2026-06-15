# راهنمای بهینه‌سازی عملکرد اکو نوژین

**تاریخ:** 2026-06-15
**نسخه:** 1.0.0

## فهرست مطالب

1. کش‌گذاری Redis
2. پردازش ناهمزمان Celery
3. بهینه‌سازی پایگاه داده
4. Load Balancing با Nginx
5. مانیتورینگ عملکرد
6. تست‌های Benchmark

---

## 1. کش‌گذاری Redis

### معماری کش

پلتفرم اکو نوژین از Redis برای کش‌گذاری چندلایه استفاده می‌کند:

- **داده‌های پایلوت:** TTL 2 ساعت
- **داده‌های داشبورد:** TTL 5 دقیقه
- **محاسبات MRV:** TTL 24 ساعت
- **نتایج شبیه‌سازی:** TTL 12 ساعت

### استفاده از Decorator

```python
from api.services.cache.redis_cache_service import cache_pilot_data

@cache_pilot_data(ttl=7200)
def get_pilot_data(pilot_id: str):
    # محاسبات سنگین
    return data
```

### آمار کش

```python
from api.services.cache.redis_cache_service import cache_service

stats = cache_service.get_stats()
print(f"Hit Rate: {stats['hit_rate']}%")
```

---

## 2. پردازش ناهمزمان Celery

### صف‌های وظایف

- **mrv:** محاسبات MRV و اعتبارات کربن
- **hydrology:** شبیه‌سازی‌های SWAT و WEAP
- **remote_sensing:** پردازش تصاویر ماهواره‌ای
- **notifications:** ارسال اعلان‌ها

### اجرای وظایف

```python
from api.tasks.mrv_tasks import calculate_mrv_report

# اجرای ناهمزمان
task = calculate_mrv_report.delay(project_id, pilot_site)
result = task.get(timeout=3600)
```

### مانیتورینگ Celery

```bash
celery -A api.tasks.celery_app flower
```

---

## 3. بهینه‌سازی پایگاه داده

### Connection Pooling

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### Indexes

ایندکس‌های بهینه‌شده برای:
- `sensor_readings(device_id, timestamp)`
- `mrv_reports(project_id, report_date)`
- `carbon_credits(project_id, status)`
- `hydrology_simulations(watershed_id, simulation_date)`

### Query Optimization

```python
from api.core.database import optimize_query_performance

query = optimize_query_performance(session.query(Model))
results = query.all()
```

---

## 4. Load Balancing با Nginx

### استراتژی Load Balancing

- **Least Connections:** توزیع بار بر اساس کمترین اتصال فعال
- **Health Checks:** بررسی سلامت سرورها هر 30 ثانیه
- **Failover:** سرور پشتیبان در صورت خطا

### Rate Limiting

- **API:** 100 درخواست در ثانیه
- **Login:** 5 درخواست در دقیقه

### Caching

```nginx
proxy_cache_path /var/cache/nginx levels=1:2
    keys_zone=api_cache:10m
    max_size=1g
    inactive=60m;
```

---

## 5. مانیتورینگ عملکرد

### معیارهای سیستم

```python
from api.services.monitoring.performance_monitor import performance_monitor

metrics = performance_monitor.get_system_metrics()
print(f"CPU: {metrics['cpu_percent']}%")
print(f"Memory: {metrics['memory_percent']}%")
```

### معیارهای توابع

```python
@performance_monitor.measure_execution_time("heavy_function")
def heavy_function():
    # محاسبات سنگین
    pass
```

### Prometheus + Grafana

```bash
docker-compose -f docker-compose.prod.yml up prometheus grafana
```

- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3000

---

## 6. تست‌های Benchmark

### اجرای تست‌ها

```bash
pytest tests/performance/ -v
```

### معیارهای هدف

| معیار | هدف |
|-------|------|
| Cache Hit Rate | > 80% |
| API Response Time | < 200ms |
| Database Query Time | < 100ms |
| Concurrent Users | 1000+ |
| System Uptime | 99.9% |

---

## مقیاس‌پذیری جهانی

پلتفرم اکو نوژین برای خدمت‌رسانی به:

- **12 پایلوت** از 4 قاره
- **10,000+ کاربر** هم‌زمان
- **1,000,000+ درخواست** در روز
- **100+ TB داده** در سال

بهینه‌سازی شده است.