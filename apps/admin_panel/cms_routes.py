"""Proxy routes: FastAPI admin → Strapi CMS."""

from __future__ import annotations

from typing import Annotated, Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from apps.admin_panel.integrations.cms import get_cms_service
from apps.users.dependencies import get_current_active_superuser

router = APIRouter(prefix="/admin/cms", tags=["Admin CMS Bridge"])

CurrentSuperuser = Annotated[object, Depends(get_current_active_superuser)]


@router.get("/health")
async def cms_health(current_user: CurrentSuperuser):
    svc = get_cms_service()
    if not svc:
        raise HTTPException(status_code=503, detail="CMS service not configured")
    return await svc.health()


@router.get("/content-types")
async def cms_content_types(current_user: CurrentSuperuser):
    svc = get_cms_service()
    return await svc.list_content_types()


@router.get("/content/{content_type}")
async def cms_list(
    content_type: str,
    current_user: CurrentSuperuser,
    page: int = Query(1, ge=1),
    pageSize: int = Query(25, ge=1, le=100),
):
    svc = get_cms_service()
    try:
        return await svc.get_content_items(
            content_type,
            params={"pagination[page]": page, "pagination[pageSize]": pageSize},
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"CMS upstream error: {e}")


@router.get("/content/{content_type}/{item_id}")
async def cms_get(content_type: str, item_id: int, current_user: CurrentSuperuser):
    svc = get_cms_service()
    try:
        return await svc.get_content_item(content_type, item_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"CMS upstream error: {e}")


@router.post("/content/{content_type}", status_code=status.HTTP_201_CREATED)
async def cms_create(
    content_type: str,
    body: Dict[str, Any],
    current_user: CurrentSuperuser,
):
    svc = get_cms_service()
    try:
        return await svc.create_content_item(content_type, body)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"CMS upstream error: {e}")


@router.put("/content/{content_type}/{item_id}")
async def cms_update(
    content_type: str,
    item_id: int,
    body: Dict[str, Any],
    current_user: CurrentSuperuser,
):
    svc = get_cms_service()
    try:
        return await svc.update_content_item(content_type, item_id, body)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"CMS upstream error: {e}")


@router.delete("/content/{content_type}/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cms_delete(content_type: str, item_id: int, current_user: CurrentSuperuser):
    svc = get_cms_service()
    try:
        ok = await svc.delete_content_item(content_type, item_id)
        if not ok:
            raise HTTPException(status_code=502, detail="Delete failed")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"CMS upstream error: {e}")
