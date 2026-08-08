# ==============================================================================
# PATCH FILE: Performance Optimizations (Cursor Pagination & Redis Caching)
# TARGET FILES: apps\admin_panel\repository.py  AND  apps\admin_panel\service.py
# ==============================================================================

# ------------------------------------------------------------------------------
# بخش ۱: اصلاح Repository (جایگزین متد قدیمی Offset-based در repository.py)
# ------------------------------------------------------------------------------
from sqlalchemy import desc, func, select

# فرض بر این است که مدل AuditLog ایمپورت شده است


class AuditLogRepository:
    async def get_logs_cursor(
        self, db: AsyncSession, cursor: str | None, limit: int = 50, filters: dict = None
    ) -> tuple[list, str | None]:
        """
        پیادهسازی Cursor-based Pagination برای جلوگیری از کندی در دیتاستهای بزرگ.
        """
        stmt = select(AuditLog).order_by(desc(AuditLog.id))

        if filters:
            if filters.get("event_type"):
                stmt = stmt.where(AuditLog.event_type == filters["event_type"])
            if filters.get("actor_email"):
                stmt = stmt.where(AuditLog.actor_email == filters["actor_email"])

        # منطق اصلی Cursor: دریافت رکوردهایی که ID آنها کمتر از Cursor فعلی است
        if cursor:
            stmt = stmt.where(AuditLog.id < int(cursor))

        # دریافت limit + 1 برای تشخیص وجود صفحه بعدی
        stmt = stmt.limit(limit + 1)

        result = await db.execute(stmt)
        logs = list(result.scalars().all())

        has_next_page = len(logs) > limit
        if has_next_page:
            logs = logs[:limit]  # حذف رکورد اضافی که فقط برای چک کردن بود

        next_cursor = str(logs[-1].id) if logs and has_next_page else None

        return logs, next_cursor


# ------------------------------------------------------------------------------
# بخش ۲: اصلاح Service (افزودن Caching به داشبورد در service.py)
# ------------------------------------------------------------------------------
import json

import redis.asyncio as aioredis

from apps.shared_core.config import settings  # تنظیمات پروه شما

# ایجاد یک Connection Pool مشترک برای Redis (خارج از کلاس برای استفاده مجدد)
redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)


class DashboardService:
    async def get_overview_stats(self, db: AsyncSession) -> dict:
        cache_key = "admin:dashboard:overview_stats"

        # ۱. تلاش برای خواندن از کش (Cache Hit)
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)

        # ۲. محاسبات سنگین دیتابیس (Cache Miss)
        total_users_stmt = select(func.count(User.id))
        active_users_stmt = select(func.count(User.id)).where(User.is_active == True)

        total_users = await db.scalar(total_users_stmt) or 0
        active_users = await db.scalar(active_users_stmt) or 0

        stats = {
            "total_users": total_users,
            "active_users": active_users,
            # سایر آمارها را اینجا اضافه کنید
        }

        # ۳. ذخیره در کش با TTL (مثلا ۳۰۰ ثانیه = ۵ دقیقه)
        await redis_client.setex(cache_key, 300, json.dumps(stats))

        return stats

    # نکته مهم برای توسعهدهنده:
    # هرگاه کاربر جدیدی ثبتنام کرد یا تنظیماتی تغییر کرد باید در سرویس مربوطه
    # دستور await redis_client.delete("admin:dashboard:overview_stats") فراخوانی شود
    # تا کش باطل (Invalidate) گردد.
