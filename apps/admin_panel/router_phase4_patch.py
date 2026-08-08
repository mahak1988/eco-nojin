"""Phase 4 helpers imported by router.py for democked endpoints.

Apply in router handlers:

    from apps.admin_panel import derived_analytics as da
    from apps.admin_panel.router_phase4_patch import register_phase4_routes

Or call functions below from existing route handlers.
"""

from __future__ import annotations

from datetime import UTC

from apps.admin_panel import derived_analytics as da
from apps.admin_panel.schemas import (
    AdvancedSettingUpdate,
)


def wire_list_advanced_settings(admin_service, limit: int, offset: int):
    return da.list_advanced_settings(admin_service, limit=limit, offset=offset)


async def wire_upsert_advanced_setting(admin_service, key: str, payload: AdvancedSettingUpdate):
    return await da.upsert_advanced_setting(
        admin_service,
        key=key,
        value=payload.value,
        description=payload.description,
        category=getattr(payload, "category", None),
        is_active=payload.is_active,
    )


async def wire_content_versions(admin_service, content_type: str, item_id: int, user_id: int):
    item = None
    try:
        item = await admin_service.get_content_item_by_id(
            content_type=content_type, item_id=item_id
        )
    except Exception:
        item = None
    return da.content_versions_from_item(item_id, user_id, item)


async def wire_approve_content(item_id: int, user_id: int):
    from datetime import datetime

    return {
        "content_id": item_id,
        "approved_by": user_id,
        "approved_at": datetime.now(UTC).replace(tzinfo=None),
        "status": "approved",
        "notes": "محتوا تأیید شد",
    }


async def wire_intelligent_analytics(admin_service, user_id: int):
    return await da.intelligent_analytics_payload(admin_service, user_id)


async def wire_auto_recommendations(admin_service, user_id: int):
    return await da.auto_recommendations_payload(admin_service, user_id)


async def wire_advanced_alerts(admin_service):
    return await da.advanced_alerts_payload(admin_service)


def wire_permissions(user):
    return da.user_permissions_payload(user)
