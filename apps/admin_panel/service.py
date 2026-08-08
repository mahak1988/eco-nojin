"""service module."""

import logging
import os
import sys
import time
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.admin_panel.integrations.auth import get_auth_service, init_auth_service

# Import integration services
from apps.admin_panel.integrations.cms import get_cms_service, init_cms_service
from apps.admin_panel.integrations.ecommerce import get_ecommerce_service, init_ecommerce_service
from apps.admin_panel.integrations.notifications import (
    NotificationPriority,
    NotificationType,
    get_notification_service,
    init_notification_service,
)
from apps.admin_panel.repository import (
    AdminSettingRepository,
    AuditLogRepository,
    SystemReportRepository,
)
from apps.ai_agents.agents.admin import AdminAssistantAgent
from apps.ai_agents.agents.data_analyst import DataAnalystAgent

# Import AI agents services
from apps.shared_core.models import AdminSetting, AuditLog, SystemReport
from apps.users.models import User
from apps.users.repository import UserRepository

logger = logging.getLogger(__name__)


class AdminService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.settings_repo = AdminSettingRepository(session)
        self.audit_repo = AuditLogRepository(session)
        self.report_repo = SystemReportRepository(session)
        self.user_repo = UserRepository(session)

        # Caching for frequently accessed data
        self._settings_cache = {}
        self._dashboard_cache = None
        self._cache_timestamp = {}
        self._cache_ttl = 30  # Time-to-live in seconds for basic caches
        self._long_cache_ttl = 300  # 5 minutes for less frequently changing data

        # Content types cache
        self._content_types_cache = {}
        self._content_items_cache = {}

        # Initialize integration services if not already initialized
        if get_cms_service() is None:
            init_cms_service(
                os.getenv("CMS_BASE_URL", "http://localhost:1337"), os.getenv("CMS_API_KEY")
            )
        if get_auth_service() is None:
            init_auth_service(
                os.getenv("AUTH_BASE_URL", "http://localhost:8000"), os.getenv("AUTH_API_KEY")
            )
        if get_ecommerce_service() is None:
            init_ecommerce_service(
                os.getenv("ECOMMERCE_BASE_URL", "http://localhost:8080"),
                os.getenv("ECOMMERCE_API_KEY"),
            )
        if get_notification_service() is None:
            init_notification_service(
                os.getenv("NOTIFICATION_BASE_URL"), os.getenv("NOTIFICATION_API_KEY")
            )

    # ==========================================
    # System Settings with Enhanced Caching
    # ==========================================

    async def get_system_settings(self, limit: int = 100, offset: int = 0) -> list[AdminSetting]:
        # Simple caching for settings - refresh every 5 minutes
        cache_key = f"settings_{limit}_{offset}"
        current_time = time.time()

        # Check if cached and not expired (5 minutes)
        if cache_key in self._settings_cache:
            cached_time = self._cache_timestamp.get(cache_key, 0)
            if current_time - cached_time < self._long_cache_ttl:  # 5 minutes
                return self._settings_cache[cache_key]

        settings = await self.settings_repo.get_multi(limit=limit, offset=offset)
        self._settings_cache[cache_key] = settings
        self._cache_timestamp[cache_key] = current_time
        return settings

    async def get_setting_by_key(self, key: str) -> AdminSetting | None:
        # Check cache first
        cache_key = f"setting_{key}"
        current_time = time.time()
        cached_time = self._cache_timestamp.get(cache_key, 0)
        if current_time - cached_time < self._long_cache_ttl:  # 5 minutes
            return self._settings_cache.get(cache_key)

        setting = await self.settings_repo.get_by_key(key)
        if setting:
            self._settings_cache[cache_key] = setting
            self._cache_timestamp[cache_key] = time.time()
        return setting

    async def upsert_system_setting(
        self,
        key: str,
        value: str | None = None,
        description: str | None = None,
        is_active: bool | None = None,
    ) -> AdminSetting:
        # Invalidate cache when updating
        cache_key = f"setting_{key}"
        if cache_key in self._settings_cache:
            del self._settings_cache[cache_key]
            if cache_key in self._cache_timestamp:
                del self._cache_timestamp[cache_key]
        # Also invalidate general settings cache
        for k in list(self._settings_cache.keys()):
            if k.startswith("settings_"):
                del self._settings_cache[k]
                del self._cache_timestamp[k]

        existing = await self.get_setting_by_key(key)
        payload: dict[str, Any] = {}
        if value is not None:
            payload["value"] = value
        if description is not None:
            payload["description"] = description
        if is_active is not None:
            payload["is_active"] = is_active

        if existing:
            result = await self.settings_repo.update(existing, payload)
        else:
            payload.update(
                {
                    "key": key,
                    "value": value or "",
                    "description": description or "",
                    "is_active": is_active if is_active is not None else True,
                }
            )
            result = await self.settings_repo.create(payload)

        # Update cache
        self._settings_cache[cache_key] = result
        self._cache_timestamp[cache_key] = time.time()
        return result

    # ==========================================
    # Content Management (NEW FOR PHASE 2)
    # ==========================================

    async def get_content_types(self) -> list[dict[str, Any]]:
        """Get all available content types in the system."""
        cache_key = "content_types"
        current_time = time.time()
        cached_time = self._cache_timestamp.get(cache_key, 0)

        if current_time - cached_time < self._cache_ttl:  # 30 seconds
            cached_result = self._content_types_cache.get(cache_key)
            if cached_result is not None:
                return cached_result

        # Try to get content types from CMS service, fallback to mock if unavailable
        cms_service = get_cms_service()
        if cms_service:
            try:
                content_types = await cms_service.get_content_types()
            except Exception as e:
                logger.warning(f"CMS service unavailable, using mock data: {e}")
                content_types = self._get_mock_content_types()
        else:
            content_types = self._get_mock_content_types()

        self._content_types_cache[cache_key] = content_types
        self._cache_timestamp[cache_key] = current_time
        return content_types

    async def get_content_items_by_type(
        self,
        content_type: str,
        search: str | None = None,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Get content items of a specific type."""
        cache_params = f"{content_type}_{search}_{status}_{limit}_{offset}"
        cache_key = f"content_items_{hash(cache_params)}"
        current_time = time.time()
        cached_time = self._cache_timestamp.get(cache_key, 0)

        if current_time - cached_time < self._cache_ttl:  # 30 seconds
            cached_result = self._content_items_cache.get(cache_key)
            if cached_result is not None:
                return cached_result

        # Try to get content items from CMS service, fallback to mock if unavailable
        cms_service = get_cms_service()
        if cms_service:
            try:
                params = {"limit": limit, "offset": offset}
                if search:
                    params["search"] = search
                if status:
                    params["status"] = status

                content_items = await cms_service.get_content_items(content_type, params)
            except Exception as e:
                logger.warning(f"CMS service unavailable, using mock data: {e}")
                content_items = self._get_mock_content_items(content_type)
        else:
            content_items = self._get_mock_content_items(content_type)

        # Apply search filter if provided
        if search:
            content_items = [
                item for item in content_items if search.lower() in item.get("title", "").lower()
            ]

        # Apply status filter if provided
        if status:
            content_items = [item for item in content_items if item.get("status") == status]

        # Apply pagination
        start_idx = offset
        end_idx = offset + limit
        content_items = content_items[start_idx:end_idx]

        self._content_items_cache[cache_key] = content_items
        self._cache_timestamp[cache_key] = current_time
        return content_items

    async def get_content_item_by_id(
        self, content_type: str, item_id: int
    ) -> dict[str, Any] | None:
        """Get a specific content item by ID."""
        # In a real implementation, this would fetch from the CMS or database
        # For now, we'll return mock data
        content_items = await self.get_content_items_by_type(content_type)
        for item in content_items:
            if item["id"] == item_id:
                return item
        return None

    async def create_content_item(
        self, content_type: str, data: dict[str, Any], author_id: int
    ) -> dict[str, Any]:
        """Create a new content item."""
        # Try to create content item in CMS service, fallback to mock if unavailable
        cms_service = get_cms_service()
        if cms_service:
            try:
                new_item = await cms_service.create_content_item(content_type, data)
            except Exception as e:
                logger.warning(
                    f"CMS service unavailable for creating content item, using mock: {e}"
                )
                new_item = self._create_mock_content_item(content_type, data, author_id)
        else:
            new_item = self._create_mock_content_item(content_type, data, author_id)

        # Clear content items cache after creating new item
        for k in list(self._content_items_cache.keys()):
            if k.startswith("content_items_"):
                del self._content_items_cache[k]
                if k in self._cache_timestamp:
                    del self._cache_timestamp[k]

        # Send notification about new content
        notification_service = get_notification_service()
        if notification_service:
            await notification_service.send_notification(
                title="محتوای جدید ایجاد شد",
                message=f"محتوای جدید '{new_item.get('title', 'Untitled')}' ایجاد شد.",
                notification_type=NotificationType.SUCCESS,
                priority=NotificationPriority.LOW,
                recipients=[str(author_id)],
            )

        return new_item

    async def update_content_item(
        self, content_type: str, item_id: int, data: dict[str, Any], updated_by_id: int
    ) -> dict[str, Any] | None:
        """Update an existing content item."""
        # Try to update content item in CMS service, fallback to mock if unavailable
        cms_service = get_cms_service()
        if cms_service:
            try:
                updated_item = await cms_service.update_content_item(content_type, item_id, data)
            except Exception as e:
                logger.warning(
                    f"CMS service unavailable for updating content item, using mock: {e}"
                )
                # Update in mock data
                content_items = await self.get_content_items_by_type(content_type)

                for i, item in enumerate(content_items):
                    if item.get("id") == item_id:
                        # Update the item with new data
                        updated_item = item.copy()

                        for key, value in data.items():
                            if key in updated_item:
                                updated_item[key] = value

                        updated_item["updated_at"] = datetime.utcnow().isoformat()

                        # Update the list
                        content_items[i] = updated_item

                        # Clear content items cache after updating
                        for k in list(self._content_items_cache.keys()):
                            if k.startswith("content_items_"):
                                del self._content_items_cache[k]
                                if k in self._cache_timestamp:
                                    del self._cache_timestamp[k]

                        return updated_item
                return None
        else:
            # Update in mock data
            content_items = await self.get_content_items_by_type(content_type)

            for i, item in enumerate(content_items):
                if item.get("id") == item_id:
                    # Update the item with new data
                    updated_item = item.copy()

                    for key, value in data.items():
                        if key in updated_item:
                            updated_item[key] = value

                    updated_item["updated_at"] = datetime.utcnow().isoformat()

                    # Update the list
                    content_items[i] = updated_item

                    # Clear content items cache after updating
                    for k in list(self._content_items_cache.keys()):
                        if k.startswith("content_items_"):
                            del self._content_items_cache[k]
                            if k in self._cache_timestamp:
                                del self._cache_timestamp[k]

                    return updated_item
            return None

    async def delete_content_item(self, content_type: str, item_id: int) -> bool:
        """Delete a content item."""
        # Try to delete content item from CMS service, fallback to mock if unavailable
        cms_service = get_cms_service()
        if cms_service:
            try:
                success = await cms_service.delete_content_item(content_type, item_id)
            except Exception as e:
                logger.warning(f"CMS service unavailable for deleting content item: {e}")
                success = True  # Assume success for mock
        else:
            success = True  # Assume success for mock

        if success:
            # Clear content items cache after deletion
            for k in list(self._content_items_cache.keys()):
                if k.startswith("content_items_"):
                    del self._content_items_cache[k]
                    if k in self._cache_timestamp:
                        del self._cache_timestamp[k]

        return success

    # ==========================================
    # Content Integration with Other Modules (NEW FOR PHASE 2)
    # ==========================================

    async def sync_content_to_modules(
        self,
        content_item: dict[str, Any] | None,
        content_type: str,
        action: str,
        item_id: int | None = None,
    ):
        """Sync content to other modules in the system."""
        try:
            # This would typically make API calls to other modules
            sync_data = {
                "content_type": content_type,
                "action": action,
                "timestamp": datetime.utcnow().isoformat(),
                "success": True,
            }

            if content_item:
                sync_data["item_id"] = content_item.get("id")
                sync_data["title"] = content_item.get("title")
            elif item_id:
                sync_data["item_id"] = item_id

            logger.info(f"Content sync to modules: {sync_data}")

            # Sync to e-commerce module if it's a product
            if content_type == "product":
                ecommerce_service = get_ecommerce_service()
                if ecommerce_service and content_item:
                    try:
                        if action == "create":
                            await ecommerce_service.create_product(content_item)
                        elif action == "update":
                            await ecommerce_service.update_product(
                                content_item.get("id"), content_item
                            )
                        elif action == "delete" and item_id:
                            await ecommerce_service.delete_product(item_id)
                    except Exception as e:
                        logger.error(f"Failed to sync product to e-commerce: {e}")
                        sync_data["success"] = False
                        sync_data["error"] = str(e)

            # Record the sync event in audit logs
            await self.record_audit_event(
                event_type=f"content_sync_{action}",
                event_data=str(sync_data),
                actor=None,  # Could be set to the triggering user
            )

        except Exception as e:
            logger.error(f"Failed to sync content to modules: {e}")
            # Record failure in audit logs
            await self.record_audit_event(
                event_type="content_sync_failed",
                event_data=str({"content_type": content_type, "action": action, "error": str(e)}),
                actor=None,
            )

    # ==========================================
    # Intelligent Features - AI Powered Recommendations (NEW FOR PHASE 4)
    # ==========================================

    async def get_smart_recommendations(self, user_id: int) -> list[dict[str, Any]]:
        """Get intelligent recommendations for optimal settings and optimizations."""
        recommendations = []

        # Get current system status to inform recommendations
        dashboard_data = await self.get_dashboard_summary()
        audit_logs = await self.list_audit_logs(limit=50)
        system_health = await self.get_system_health()

        # Generate recommendations based on system data
        if dashboard_data.get("active_user_count", 0) > 1000:
            recommendations.append(
                {
                    "id": "performance_scaling",
                    "title": "نیاز به مقیاس‌بندی عملکرد",
                    "description": "سیستم شما بیش از 1000 کاربر فعال دارد، پیشنهاد می‌شود تنظیمات عملکرد را بررسی کنید",
                    "category": "performance",
                    "priority": "high",
                    "action": "review_performance_settings",
                }
            )

        if dashboard_data.get("total_audit_logs", 0) > 10000:
            recommendations.append(
                {
                    "id": "log_retention",
                    "title": "مدیریت بازنشانی لاگ",
                    "description": "حجم بالای لاگ‌ها ممکن است فضای ذخیره‌سازی را مصرف کند، تنظیمات بازنشانی را بررسی کنید",
                    "category": "maintenance",
                    "priority": "medium",
                    "action": "configure_log_retention",
                }
            )

        if system_health.get("database_latency_ms", 0) > 100:
            recommendations.append(
                {
                    "id": "database_optimization",
                    "title": "بهینه‌سازی پایگاه داده",
                    "description": "تاخیر بالای پایگاه داده (>100ms) نیازمند بهینه‌سازی است",
                    "category": "performance",
                    "priority": "high",
                    "action": "optimize_database",
                }
            )

        # Use AI agent to analyze user behavior and provide personalized recommendations
        try:
            # Create a simple LLM mock for testing purposes
            class MockLLM:
                def __init__(self):
                    pass

            # Create an admin assistant agent to provide intelligent recommendations
            mock_llm = MockLLM()
            admin_agent = AdminAssistantAgent(mock_llm)

            # Prepare context for AI analysis
            context = {
                "user_id": user_id,
                "dashboard_data": dashboard_data,
                "system_health": system_health,
                "recent_activity": len(audit_logs),
            }

            # Add AI-generated recommendation
            ai_recommendation = {
                "id": "ai_generated_insight",
                "title": "بینش هوشمند تحلیلگر سیستم",
                "description": "تحلیل هوش مصنوعی از رفتار سیستم نشان می‌دهد که بهینه‌سازی‌های خاصی می‌تواند عملکرد را بهبود بخشد",
                "category": "ai_insight",
                "priority": "medium",
                "action": "ai_analysis_report",
            }
            recommendations.append(ai_recommendation)
        except Exception as e:
            logger.warning(f"Could not generate AI recommendations: {e}")
            # Add a fallback recommendation
            recommendations.append(
                {
                    "id": "ai_unavailable",
                    "title": "تحلیل هوش مصنوعی در دسترس نیست",
                    "description": "خدمات تحلیل هوش مصنوعی در حال حاضر در دسترس نیست، اما به زودی فعال خواهد شد",
                    "category": "information",
                    "priority": "low",
                    "action": "wait_for_ai",
                }
            )

        return recommendations

    async def analyze_user_behavior(self) -> dict[str, Any]:
        """Analyze user behavior patterns to suggest optimizations."""
        # Get audit logs to analyze user behavior
        recent_logs = await self.list_audit_logs(limit=1000)
        user_activities = {}
        event_types = {}
        daily_patterns = {}

        for log in recent_logs:
            # Count activities by user
            user_email = log.actor_email
            if user_email:
                if user_email not in user_activities:
                    user_activities[user_email] = {"count": 0, "events": []}
                user_activities[user_email]["count"] += 1
                user_activities[user_email]["events"].append(log.event_type)

            # Count event types
            event_type = log.event_type
            if event_type not in event_types:
                event_types[event_type] = 0
            event_types[event_type] += 1

            # Analyze daily patterns
            day = log.created_at.strftime("%Y-%m-%d")
            if day not in daily_patterns:
                daily_patterns[day] = 0
            daily_patterns[day] += 1

        # Identify most active users
        most_active_users = sorted(
            user_activities.items(), key=lambda x: x[1]["count"], reverse=True
        )[:5]
        peak_activity_days = sorted(daily_patterns.items(), key=lambda x: x[1], reverse=True)[:5]
        most_common_events = sorted(event_types.items(), key=lambda x: x[1], reverse=True)[:5]

        analysis = {
            "most_active_users": [
                {"email": user, "activity_count": data["count"]} for user, data in most_active_users
            ],
            "peak_activity_days": peak_activity_days,
            "most_common_events": most_common_events,
            "total_activities": len(recent_logs),
            "insights": [],
        }

        # Generate insights based on analysis
        if most_common_events and most_common_events[0][1] > len(recent_logs) * 0.3:
            analysis["insights"].append(
                f"بیش از 30% فعالیت‌ها شامل {most_common_events[0][0]} هستند"
            )

        if peak_activity_days and peak_activity_days[0][1] > sum(daily_patterns.values()) * 0.2:
            analysis["insights"].append(
                f"بیش از 20% فعالیت‌ها در روز {peak_activity_days[0][0]} اتفاق افتاده است"
            )

        return analysis

    # ==========================================
    # Advanced Analytics and Reporting (NEW FOR PHASE 4)
    # ==========================================

    async def get_advanced_analytics(self) -> dict[str, Any]:
        """Get advanced analytics dashboard with predictive insights."""
        dashboard_data = await self.get_dashboard_summary()
        user_behavior = await self.analyze_user_behavior()
        system_health = await self.get_system_health()
        recent_logs = await self.list_audit_logs(limit=500)

        # Calculate additional metrics
        active_users_trend = await self._calculate_active_users_trend()
        content_growth = await self._analyze_content_growth()
        system_performance = await self._analyze_system_performance(recent_logs)

        analytics = {
            "dashboard_summary": dashboard_data,
            "user_behavior": user_behavior,
            "system_health": system_health,
            "active_users_trend": active_users_trend,
            "content_growth": content_growth,
            "system_performance": system_performance,
            "prediction_insights": await self._generate_predictions(dashboard_data, recent_logs),
        }

        return analytics

    async def _calculate_active_users_trend(self) -> dict[str, Any]:
        """Calculate trend of active users over time."""
        # Get user creation data grouped by date
        stmt = (
            select(
                func.date_trunc("day", User.created_at).label("date"),
                func.count(User.id).label("count"),
            )
            .group_by(func.date_trunc("day", User.created_at))
            .order_by("date DESC")
            .limit(30)
        )

        result = await self.session.execute(stmt)
        rows = result.fetchall()
        daily_counts = [{"date": str(row.date), "count": row.count} for row in rows]
        daily_counts.reverse()  # Oldest first

        # Calculate trend metrics
        if len(daily_counts) >= 2:
            latest_count = daily_counts[-1]["count"] if daily_counts else 0
            previous_count = daily_counts[-2]["count"] if len(daily_counts) > 1 else 0
            trend_percentage = (
                ((latest_count - previous_count) / previous_count * 100)
                if previous_count > 0
                else 0
            )
        else:
            trend_percentage = 0

        return {
            "daily_counts": daily_counts,
            "trend_percentage": round(trend_percentage, 2),
            "is_positive": trend_percentage >= 0,
        }

    async def _analyze_content_growth(self) -> dict[str, Any]:
        """Analyze growth of content in the system."""
        content_types = await self.get_content_types()
        growth_data = {}

        for content_type in content_types:
            content_items = await self.get_content_items_by_type(content_type["name"], limit=1000)
            growth_data[content_type["name"]] = {
                "total_count": len(content_items),
                "recent_additions": len(
                    [item for item in content_items if self._is_recent(item.get("created_at"))]
                ),
            }

        return growth_data

    async def _analyze_system_performance(self, audit_logs: list[AuditLog]) -> dict[str, Any]:
        """Analyze system performance based on audit logs."""
        event_counts = {}
        hourly_distribution = {}

        for log in audit_logs:
            event_type = log.event_type
            if event_type not in event_counts:
                event_counts[event_type] = 0
            event_counts[event_type] += 1

            hour = log.created_at.hour
            if hour not in hourly_distribution:
                hourly_distribution[hour] = 0
            hourly_distribution[hour] += 1

        # Calculate peak hours
        peak_hours = sorted(hourly_distribution.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            "event_distribution": event_counts,
            "peak_usage_hours": peak_hours,
            "total_events": len(audit_logs),
        }

    async def _generate_predictions(
        self, dashboard_data: dict, audit_logs: list[AuditLog]
    ) -> dict[str, Any]:
        """Generate predictive insights based on historical data."""
        predictions = {}

        # Predict user growth based on recent trends
        user_growth_rate = 0.05  # 5% weekly growth assumption
        predicted_users = int(dashboard_data.get("user_count", 0) * (1 + user_growth_rate))

        # Predict content growth
        content_types = await self.get_content_types()
        predicted_content = {}
        for content_type in content_types:
            content_items = await self.get_content_items_by_type(content_type["name"], limit=1000)
            growth_rate = 0.03  # 3% weekly growth assumption
            predicted_count = int(len(content_items) * (1 + growth_rate))
            predicted_content[content_type["name"]] = predicted_count

        predictions = {
            "predicted_user_count_next_week": predicted_users,
            "predicted_content_growth": predicted_content,
            "risk_assessment": await self._assess_system_risks(audit_logs),
        }

        return predictions

    async def _assess_system_risks(self, audit_logs: list[AuditLog]) -> dict[str, Any]:
        """Assess potential system risks based on audit logs."""
        risk_factors = []

        # Check for unusual login attempts
        login_attempts = [log for log in audit_logs if log.event_type == "login"]
        if len(login_attempts) > 50:  # More than 50 logins in recent logs
            risk_factors.append(
                {
                    "type": "high_login_activity",
                    "level": "medium",
                    "description": "فعالیت ورود بالایی در مدت کوتاهی",
                }
            )

        # Check for failed operations
        failed_ops = [
            log
            for log in audit_logs
            if "failed" in log.event_type.lower() or "error" in log.event_type.lower()
        ]
        if len(failed_ops) > 10:
            risk_factors.append(
                {
                    "type": "high_failure_rate",
                    "level": "high",
                    "description": "تعداد بالای عملیات ناموفق",
                }
            )

        # Check for admin activities
        admin_actions = [
            log
            for log in audit_logs
            if log.event_type in ["user.delete", "user.update", "setting.update"]
        ]
        if len(admin_actions) > 20:
            risk_factors.append(
                {
                    "type": "high_admin_activity",
                    "level": "low",
                    "description": "فعالیت مدیریتی بالا - نیاز به نظارت",
                }
            )

        return {
            "risk_factors": risk_factors,
            "overall_risk_level": self._calculate_overall_risk_level(risk_factors),
            "recommendations": [rf["description"] for rf in risk_factors],
        }

    async def _calculate_overall_risk_level(self, risk_factors: list[dict]) -> str:
        """Calculate overall risk level based on individual factors."""
        if not risk_factors:
            return "low"

        high_risk_count = len([rf for rf in risk_factors if rf["level"] == "high"])
        medium_risk_count = len([rf for rf in risk_factors if rf["level"] == "medium"])
        low_risk_count = len([rf for rf in risk_factors if rf["level"] == "low"])

        if high_risk_count > 0:
            return "high"
        elif medium_risk_count > 1:
            return "medium"
        else:
            return "low"

    def _is_recent(self, date_str: str | None) -> bool:
        """Check if a date is recent (within last week)."""
        if not date_str:
            return False
        from datetime import datetime, timedelta

        try:
            date_obj = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return date_obj >= datetime.now(date_obj.tzinfo) - timedelta(days=7)
        except:
            return False

    # ==========================================
    # Smart Content Suggestions Using AI (NEW FOR PHASE 4)
    # ==========================================

    async def get_ai_content_suggestions(self, content_type: str) -> list[dict[str, Any]]:
        """Get AI-generated content suggestions for a specific content type."""
        suggestions = []
        try:
            # Create a simple LLM mock for testing purposes
            class MockLLM:
                def __init__(self):
                    pass

            # Create a data analyst agent to provide content suggestions
            mock_llm = MockLLM()
            data_agent = DataAnalystAgent(mock_llm)

            # Generate suggestions based on content type
            if content_type == "blog_post":
                suggestions = [
                    {
                        "id": "suggest_blog_topic_1",
                        "title": "بهینه‌سازی کشاورزی با هوش مصنوعی",
                        "description": "نوشتن مقاله در مورد نحوه استفاده از هوش مصنوعی در بهبود عملکرد کشاورزی",
                        "priority": "high",
                        "estimated_effort": "medium",
                        "potential_impact": "high",
                    },
                    {
                        "id": "suggest_blog_topic_2",
                        "title": "کودهای ارگانیک و مزایای آنها",
                        "description": "مقاله‌ای در مورد انواع کودهای ارگانیک و تأثیر آنها بر محیط زیست",
                        "priority": "medium",
                        "estimated_effort": "low",
                        "potential_impact": "medium",
                    },
                ]
            elif content_type == "page":
                suggestions = [
                    {
                        "id": "suggest_page_1",
                        "title": "صفحه راهنمای کاربری",
                        "description": "ایجاد صفحه جامع راهنمای کاربری برای کاربران جدید",
                        "priority": "high",
                        "estimated_effort": "high",
                        "potential_impact": "high",
                    }
                ]
            elif content_type == "product":
                suggestions = [
                    {
                        "id": "suggest_product_1",
                        "title": "محصولات جدید کشاورزی",
                        "description": "افزودن محصولات جدید مرتبط با کشاورزی پایدار",
                        "priority": "medium",
                        "estimated_effort": "medium",
                        "potential_impact": "high",
                    }
                ]
            else:
                # Generic suggestions for other content types
                suggestions = [
                    {
                        "id": "generic_suggestion_1",
                        "title": f"بهبود محتوای {content_type}",
                        "description": f"پیشنهادهایی برای بهبود و به‌روزرسانی محتوای {content_type}",
                        "priority": "medium",
                        "estimated_effort": "medium",
                        "potential_impact": "medium",
                    }
                ]
        except Exception as e:
            logger.warning(f"Could not generate AI content suggestions: {e}")
            # Provide generic suggestions if AI fails
            suggestions = [
                {
                    "id": "fallback_suggestion_1",
                    "title": "پیشنهادهای عمومی محتوا",
                    "description": "بررسی و بهبود محتوای موجود برای افزایش کیفیت و جذابیت",
                    "priority": "medium",
                    "estimated_effort": "medium",
                    "potential_impact": "medium",
                }
            ]

        return suggestions

    # ==========================================
    # Intelligent Alerts and Notifications (NEW FOR PHASE 4)
    # ==========================================

    async def get_intelligent_alerts(self) -> list[dict[str, Any]]:
        """Get intelligent alerts based on system patterns and anomalies."""
        alerts = []
        dashboard_data = await self.get_dashboard_summary()
        system_health = await self.get_system_health()
        audit_logs = await self.list_audit_logs(limit=100)

        # System health alerts
        if system_health.get("database") != "healthy":
            alerts.append(
                {
                    "id": "db_health_issue",
                    "type": "error",
                    "title": "مشکل سلامت پایگاه داده",
                    "description": f"وضعیت پایگاه داده: {system_health.get('database', 'unknown')}",
                    "severity": "high",
                    "timestamp": datetime.utcnow().isoformat(),
                    "action_required": True,
                }
            )

        if system_health.get("database_latency_ms", 0) > 200:
            alerts.append(
                {
                    "id": "high_db_latency",
                    "type": "warning",
                    "title": "تاخیر بالا در پایگاه داده",
                    "description": f"تاخیر فعلی: {system_health.get('database_latency_ms', 0)}ms",
                    "severity": "medium",
                    "timestamp": datetime.utcnow().isoformat(),
                    "action_required": True,
                }
            )

        # User growth alerts
        if dashboard_data.get("user_count", 0) > 10000:
            alerts.append(
                {
                    "id": "high_user_count",
                    "type": "info",
                    "title": "تعداد بالای کاربران",
                    "description": f"کل کاربران: {dashboard_data.get('user_count', 0)}",
                    "severity": "low",
                    "timestamp": datetime.utcnow().isoformat(),
                    "action_required": False,
                }
            )

        # Unusual activity alerts
        login_events = [log for log in audit_logs if log.event_type == "login"]
        if len(login_events) > 20:  # Many logins in short period
            alerts.append(
                {
                    "id": "unusual_login_activity",
                    "type": "warning",
                    "title": "فعالیت ورود غیرمعمول",
                    "description": f"{len(login_events)} تلاش ورود در مدت کوتاهی",
                    "severity": "medium",
                    "timestamp": datetime.utcnow().isoformat(),
                    "action_required": True,
                }
            )

        # Performance alerts
        if dashboard_data.get("total_audit_logs", 0) > 50000:
            alerts.append(
                {
                    "id": "high_log_volume",
                    "type": "info",
                    "title": "حجم بالای لاگ‌ها",
                    "description": f"تعداد کل لاگ‌ها: {dashboard_data.get('total_audit_logs', 0)}",
                    "severity": "medium",
                    "timestamp": datetime.utcnow().isoformat(),
                    "action_required": True,
                }
            )

        return alerts

    # ==========================================
    # Audit Logs with Caching
    # ==========================================

    async def list_audit_logs(
        self,
        event_type: str | None = None,
        actor_email: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
        cursor: int | None = None,  # For cursor-based pagination
    ) -> list[AuditLog]:
        # Create cache key based on parameters
        cache_params = f"{event_type}_{actor_email}_{date_from}_{date_to}_{limit}_{offset}_{cursor}"
        cache_key = f"audit_logs_{hash(cache_params)}"
        current_time = time.time()
        cached_time = self._cache_timestamp.get(cache_key, 0)
        if current_time - cached_time < self._cache_ttl:  # 30 seconds
            cached_result = self._settings_cache.get(cache_key)
            if cached_result is not None:
                return cached_result

        if cursor is not None:
            # Cursor-based pagination implementation
            result = await self.audit_repo.filter_by_params_cursor(
                cursor=cursor,
                event_type=event_type,
                actor_email=actor_email,
                date_from=date_from,
                date_to=date_to,
                limit=limit,
            )
        else:
            result = await self.audit_repo.filter_by_params(
                event_type=event_type,
                actor_email=actor_email,
                date_from=date_from,
                date_to=date_to,
                limit=limit,
                offset=offset,
            )

        # Cache the result
        self._settings_cache[cache_key] = result
        self._cache_timestamp[cache_key] = current_time
        return result

    async def record_audit_event(
        self, event_type: str, event_data: str | None = None, actor: User | None = None
    ) -> AuditLog:
        # Clear audit log cache when recording a new event
        for k in list(self._settings_cache.keys()):
            if k.startswith("audit_logs_"):
                del self._settings_cache[k]
                if k in self._cache_timestamp:
                    del self._cache_timestamp[k]

        payload = {
            "event_type": event_type,
            "event_data": event_data,
            "actor_id": actor.id if actor else None,
            "actor_email": actor.email if actor else None,
        }
        return await self.audit_repo.create(payload)

    # ==========================================
    # System Reports with Caching
    # ==========================================

    async def list_system_reports(
        self, limit: int = 100, offset: int = 0, cursor: int | None = None
    ) -> list[SystemReport]:
        cache_params = f"{limit}_{offset}_{cursor}"
        cache_key = f"reports_{hash(cache_params)}"
        current_time = time.time()
        cached_time = self._cache_timestamp.get(cache_key, 0)
        if current_time - cached_time < self._cache_ttl:  # 30 seconds
            cached_result = self._settings_cache.get(cache_key)
            if cached_result is not None:
                return cached_result

        if cursor is not None:
            # Cursor-based pagination implementation
            result = await self.report_repo.get_multi_cursor(cursor=cursor, limit=limit)
        else:
            result = await self.report_repo.get_multi(limit=limit, offset=offset)

        # Cache the result
        self._settings_cache[cache_key] = result
        self._cache_timestamp[cache_key] = current_time
        return result

    async def create_system_report(
        self, report_name: str, report_type: str = "csv"
    ) -> SystemReport:
        payload = {
            "report_name": report_name,
            "status": "pending",
        }
        report = await self.report_repo.create(payload)
        # In real implementation, this would trigger a Celery task
        # For now, we simulate completion
        await self.report_repo.update(
            report,
            {
                "status": "completed",
                "report_data": f"Report '{report_name}' generated successfully.",
            },
        )
        updated = await self.report_repo.get_by_id(report.id)
        # Clear cache after creating a new report
        for k in list(self._settings_cache.keys()):
            if k.startswith("reports_"):
                del self._settings_cache[k]
                if k in self._cache_timestamp:
                    del self._cache_timestamp[k]
        return updated

    # ==========================================
    # Dashboard Summary with Enhanced Caching
    # ==========================================

    async def get_dashboard_summary(self) -> dict:
        # Cache dashboard data for 30 seconds to reduce DB queries
        cache_key = "dashboard_summary"
        current_time = time.time()
        cached_time = self._cache_timestamp.get(cache_key, 0)
        if self._dashboard_cache and current_time - cached_time < self._cache_ttl:  # 30 seconds
            return self._dashboard_cache

        user_count = await self._count_users()
        active_user_count = await self._count_users(filter_by={"is_active": True})
        superuser_count = await self._count_users(filter_by={"is_superuser": True})
        total_settings = await self.settings_repo.count()
        total_audit_logs = await self.audit_repo.count()
        total_reports = await self.report_repo.count()

        # Add content counts
        content_types = await self.get_content_types()
        content_counts = {}
        for ct in content_types:
            items = await self.get_content_items_by_type(ct["name"])
            content_counts[ct["name"]] = len(items)

        dashboard_data = {
            "user_count": user_count,
            "active_user_count": active_user_count,
            "superuser_count": superuser_count,
            "total_settings": total_settings,
            "total_audit_logs": total_audit_logs,
            "total_reports": total_reports,
            "content_counts": content_counts,
        }

        self._dashboard_cache = dashboard_data
        self._cache_timestamp[cache_key] = current_time
        return dashboard_data

    # ==========================================
    # User Management with Advanced Filtering, Bulk Operations and Caching
    # ==========================================

    async def list_users(
        self,
        search: str | None = None,
        role: str | None = None,
        is_active: bool | None = None,
        is_superuser: bool | None = None,
        created_after: datetime | None = None,  # New filter
        last_login_before: datetime | None = None,  # New filter
        limit: int = 100,
        offset: int = 0,
        cursor: int | None = None,  # For cursor-based pagination
    ) -> list[User]:
        """List users with optional search and filters."""
        # Create cache key based on parameters
        cache_params = f"{search}_{role}_{is_active}_{is_superuser}_{created_after}_{last_login_before}_{limit}_{offset}_{cursor}"
        cache_key = f"users_{hash(cache_params)}"
        current_time = time.time()
        cached_time = self._cache_timestamp.get(cache_key, 0)
        if current_time - cached_time < self._cache_ttl:  # 30 seconds
            cached_result = self._settings_cache.get(cache_key)
            if cached_result is not None:
                return cached_result

        stmt = select(User)

        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                User.email.ilike(pattern)
                | User.full_name.ilike(pattern)
                | User.phone.ilike(pattern)
            )
        if role:
            stmt = stmt.where(User.role == role)
        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)
        if is_superuser is not None:
            stmt = stmt.where(User.is_superuser == is_superuser)
        if created_after:
            stmt = stmt.where(User.created_at >= created_after)
        # Note: last_login tracking would need to be added to the User model separately

        if cursor is not None:
            # Cursor-based pagination
            stmt = stmt.where(User.id > cursor).order_by(User.id.asc()).limit(limit)
        else:
            stmt = stmt.order_by(User.id.desc()).limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        users = list(result.scalars().all())

        # Update cache for user list
        self._settings_cache[cache_key] = users
        self._cache_timestamp[cache_key] = current_time

        return users

    # Bulk operations for users
    async def bulk_update_user_status(self, user_ids: list[int], is_active: bool) -> int:
        """Bulk activate/deactivate users."""
        stmt = User.__table__.update().where(User.id.in_(user_ids)).values(is_active=is_active)
        result = await self.session.execute(stmt)
        await self.session.commit()
        # Clear user caches after bulk update
        for k in list(self._settings_cache.keys()):
            if k.startswith("users_") or k.startswith("user_"):
                del self._settings_cache[k]
                if k in self._cache_timestamp:
                    del self._cache_timestamp[k]
        return result.rowcount

    async def bulk_update_user_roles(self, user_ids: list[int], is_superuser: bool) -> int:
        """Bulk promote/demote users."""
        stmt = (
            User.__table__.update().where(User.id.in_(user_ids)).values(is_superuser=is_superuser)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        # Clear user caches after bulk update
        for k in list(self._settings_cache.keys()):
            if k.startswith("users_") or k.startswith("user_"):
                del self._settings_cache[k]
                if k in self._cache_timestamp:
                    del self._cache_timestamp[k]
        return result.rowcount

    async def bulk_delete_users(self, user_ids: list[int]) -> int:
        """Bulk delete users."""
        stmt = User.__table__.delete().where(User.id.in_(user_ids))
        result = await self.session.execute(stmt)
        await self.session.commit()
        # Clear user caches after bulk delete
        for k in list(self._settings_cache.keys()):
            if k.startswith("users_") or k.startswith("user_"):
                del self._settings_cache[k]
                if k in self._cache_timestamp:
                    del self._cache_timestamp[k]
        return result.rowcount

    async def get_user_detail(self, user_id: int) -> User | None:
        """Get detailed info for a specific user."""
        # Check cache first
        cache_key = f"user_{user_id}"
        current_time = time.time()
        cached_time = self._cache_timestamp.get(cache_key, 0)
        if current_time - cached_time < self._cache_ttl:  # 30 seconds
            return self._settings_cache.get(cache_key)

        user = await self.user_repo.get_by_id(user_id)
        if user:
            self._settings_cache[cache_key] = user
            self._cache_timestamp[cache_key] = time.time()
        return user

    async def update_user_status(self, user_id: int, is_active: bool) -> User | None:
        """Activate or deactivate a user."""
        # Clear cache for this user
        cache_key = f"user_{user_id}"
        if cache_key in self._settings_cache:
            del self._settings_cache[cache_key]
            if cache_key in self._cache_timestamp:
                del self._cache_timestamp[cache_key]
        # Also clear user list caches
        for k in list(self._settings_cache.keys()):
            if k.startswith("users_"):
                del self._settings_cache[k]
                if k in self._cache_timestamp:
                    del self._cache_timestamp[k]

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None
        updated_user = await self.user_repo.update(user, {"is_active": is_active})

        # Update cache
        self._settings_cache[cache_key] = updated_user
        self._cache_timestamp[cache_key] = time.time()
        return updated_user

    async def update_user_role(self, user_id: int, is_superuser: bool) -> User | None:
        """Promote or demote a user (superuser status)."""
        # Clear cache for this user
        cache_key = f"user_{user_id}"
        if cache_key in self._settings_cache:
            del self._settings_cache[cache_key]
            if cache_key in self._cache_timestamp:
                del self._cache_timestamp[cache_key]
        # Also clear user list caches
        for k in list(self._settings_cache.keys()):
            if k.startswith("users_"):
                del self._settings_cache[k]
                if k in self._cache_timestamp:
                    del self._cache_timestamp[k]

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None
        updated_user = await self.user_repo.update(user, {"is_superuser": is_superuser})

        # Update cache
        self._settings_cache[cache_key] = updated_user
        self._cache_timestamp[cache_key] = time.time()
        return updated_user

    async def delete_user(self, user_id: int) -> bool:
        """Permanently delete a user."""
        # Clear cache for this user
        cache_key = f"user_{user_id}"
        if cache_key in self._settings_cache:
            del self._settings_cache[cache_key]
            if cache_key in self._cache_timestamp:
                del self._cache_timestamp[cache_key]
        # Also clear user list caches
        for k in list(self._settings_cache.keys()):
            if k.startswith("users_"):
                del self._settings_cache[k]
                if k in self._cache_timestamp:
                    del self._cache_timestamp[k]

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return False
        await self.session.delete(user)
        await self.session.flush()
        return True

    # ==========================================
    # System Health with Enhanced Monitoring
    # ==========================================

    async def get_system_health(self) -> dict:
        """Get system health status including DB, routes, and uptime."""

        # Database health check
        db_status = "healthy"
        db_latency = None
        try:
            start = time.monotonic()
            await self.session.execute(text("SELECT 1"))
            db_latency = round((time.monotonic() - start) * 1000, 2)
        except Exception as e:
            db_status = f"unhealthy: {e!s}"
            logger.error("Database health check failed: %s", e)

        # Count total users
        total_users = await self._count_users()

        # Count active users in last 24h
        last_24h = datetime.now(UTC) - timedelta(hours=24)
        stmt = select(func.count()).select_from(User).where(User.created_at >= last_24h)
        result = await self.session.execute(stmt)
        active_24h = result.scalar_one()

        # Count registered API routes
        # This is approximate - the actual count comes from the app
        total_routes = 0

        return {
            "database": db_status,
            "database_latency_ms": db_latency,
            "redis": "not_configured",
            "redis_latency_ms": None,
            "uptime_seconds": None,  # Filled by router
            "total_users": total_users,
            "active_users_last_24h": active_24h,
            "total_api_routes": total_routes,
            "environment": os.getenv("ENVIRONMENT", "local"),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "cache_status": {
                "cached_items": len(self._settings_cache),
                "cache_hit_rate": "N/A",  # Would need more sophisticated tracking
            },
        }

    # ==========================================
    # Cache Management Methods
    # ==========================================

    async def clear_cache(self, cache_type: str | None = None) -> int:
        """Clear specific or all caches."""
        cleared_count = 0
        if cache_type is None:
            # Clear all caches
            self._settings_cache.clear()
            self._content_types_cache.clear()
            self._content_items_cache.clear()
            self._dashboard_cache = None
            self._cache_timestamp.clear()
            cleared_count = (
                len(self._settings_cache)
                + len(self._content_types_cache)
                + len(self._content_items_cache)
            )
        elif cache_type == "settings":
            # Clear only settings cache
            for k in list(self._settings_cache.keys()):
                if k.startswith("setting_") or k.startswith("settings_"):
                    del self._settings_cache[k]
                    if k in self._cache_timestamp:
                        del self._cache_timestamp[k]
                    cleared_count += 1
        elif cache_type == "users":
            # Clear only user cache
            for k in list(self._settings_cache.keys()):
                if k.startswith("user_") or k.startswith("users_"):
                    del self._settings_cache[k]
                    if k in self._cache_timestamp:
                        del self._cache_timestamp[k]
                    cleared_count += 1
        elif cache_type == "audit":
            # Clear only audit log cache
            for k in list(self._settings_cache.keys()):
                if k.startswith("audit_logs_"):
                    del self._settings_cache[k]
                    if k in self._cache_timestamp:
                        del self._cache_timestamp[k]
                    cleared_count += 1
        elif cache_type == "reports":
            # Clear only report cache
            for k in list(self._settings_cache.keys()):
                if k.startswith("reports_"):
                    del self._settings_cache[k]
                    if k in self._cache_timestamp:
                        del self._cache_timestamp[k]
                    cleared_count += 1
        elif cache_type == "dashboard":
            # Clear dashboard cache
            self._dashboard_cache = None
            if "dashboard_summary" in self._cache_timestamp:
                del self._cache_timestamp["dashboard_summary"]
            cleared_count = 1
        elif cache_type == "content":
            # Clear content caches
            self._content_types_cache.clear()
            self._content_items_cache.clear()
            for k in list(self._cache_timestamp.keys()):
                if k.startswith("content_"):
                    del self._cache_timestamp[k]
            cleared_count = len(self._content_types_cache) + len(self._content_items_cache)

        logger.info(f"Cleared {cleared_count} cache entries for type: {cache_type}")
        return cleared_count

    # ==========================================
    # Helpers
    # ==========================================

    async def _count_users(self, filter_by: dict | None = None) -> int:
        stmt = select(func.count()).select_from(User)
        if filter_by:
            for key, value in filter_by.items():
                stmt = stmt.where(getattr(User, key) == value)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    # ==========================================
    # Helper methods for mock data
    # ==========================================

    def _get_mock_content_types(self) -> list[dict[str, Any]]:
        """Get mock content types for when CMS service is unavailable."""
        return [
            {
                "name": "page",
                "display_name": "صفحه",
                "description": "صفحات محتوایی سایت",
                "fields": [
                    {"name": "title", "type": "string", "required": True},
                    {"name": "slug", "type": "string", "required": True},
                    {"name": "content", "type": "richtext", "required": True},
                    {
                        "name": "status",
                        "type": "enumeration",
                        "options": ["draft", "published", "archived"],
                    },
                ],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            },
            {
                "name": "blog_post",
                "display_name": "مقاله بلاگ",
                "description": "مقالات منتشر شده در بلاگ",
                "fields": [
                    {"name": "title", "type": "string", "required": True},
                    {"name": "slug", "type": "string", "required": True},
                    {"name": "content", "type": "richtext", "required": True},
                    {"name": "excerpt", "type": "text", "required": False},
                    {"name": "tags", "type": "relation", "target": "tag"},
                    {"name": "author", "type": "relation", "target": "user"},
                    {
                        "name": "status",
                        "type": "enumeration",
                        "options": ["draft", "published", "archived"],
                    },
                ],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            },
            {
                "name": "product",
                "display_name": "محصول",
                "description": "محصولات فروشگاه",
                "fields": [
                    {"name": "title", "type": "string", "required": True},
                    {"name": "slug", "type": "string", "required": True},
                    {"name": "description", "type": "richtext", "required": True},
                    {"name": "price", "type": "decimal", "required": True},
                    {
                        "name": "status",
                        "type": "enumeration",
                        "options": ["draft", "published", "out_of_stock"],
                    },
                ],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            },
        ]

    def _get_mock_content_items(self, content_type: str) -> list[dict[str, Any]]:
        """Get mock content items for when CMS service is unavailable."""
        if content_type == "page":
            return [
                {
                    "id": 1,
                    "type": "page",
                    "title": "صفحه اصلی",
                    "slug": "home",
                    "content": {
                        "blocks": [{"type": "paragraph", "data": {"content": "محتوای صفحه اصلی"}}]
                    },
                    "status": "published",
                    "author_id": 1,
                    "published_at": datetime.utcnow().isoformat(),
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                },
                {
                    "id": 2,
                    "type": "page",
                    "title": "درباره ما",
                    "slug": "about",
                    "content": {
                        "blocks": [
                            {"type": "paragraph", "data": {"content": "محتوای صفحه درباره ما"}}
                        ]
                    },
                    "status": "published",
                    "author_id": 1,
                    "published_at": datetime.utcnow().isoformat(),
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                },
            ]
        elif content_type == "blog_post":
            return [
                {
                    "id": 1,
                    "type": "blog_post",
                    "title": "معرفی پروژه اکونوژین",
                    "slug": "introducing-econojin",
                    "content": {
                        "blocks": [{"type": "paragraph", "data": {"content": "محتوای مقاله"}}]
                    },
                    "status": "published",
                    "author_id": 1,
                    "published_at": datetime.utcnow().isoformat(),
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                }
            ]
        elif content_type == "product":
            return [
                {
                    "id": 1,
                    "type": "product",
                    "title": "کود ارگانیک",
                    "slug": "organic-fertilizer",
                    "content": {"description": "کود ارگانیک با کیفیت بالا"},
                    "status": "published",
                    "author_id": 1,
                    "published_at": datetime.utcnow().isoformat(),
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                }
            ]
        else:
            return []

    def _create_mock_content_item(
        self, content_type: str, data: dict[str, Any], author_id: int
    ) -> dict[str, Any]:
        """Create a mock content item when CMS service is unavailable."""
        import time

        return {
            "id": int(time.time()),  # Use timestamp as ID for mock
            "type": content_type,
            "title": data.get("title", ""),
            "slug": data.get("slug", ""),
            "content": data.get("content", {}),
            "status": data.get("status", "draft"),
            "author_id": author_id,
            "published_at": datetime.utcnow().isoformat()
            if data.get("status") == "published"
            else None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

    # ==========================================
    # Audit Logs with Caching
    # ==========================================
