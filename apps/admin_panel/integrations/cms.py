"""Strapi CMS integration for the FastAPI admin panel."""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Strapi plural API paths for core content-types
CONTENT_PATHS = {
    "page": "pages",
    "pages": "pages",
    "blog-post": "blog-posts",
    "blog_post": "blog-posts",
    "blog-posts": "blog-posts",
    "category": "categories",
    "categories": "categories",
    "tag": "tags",
    "tags": "tags",
}


class CMSIntegrationService:
    """HTTP client for Strapi REST API."""

    def __init__(self, cms_base_url: str, api_key: str | None = None):
        self.cms_base_url = cms_base_url.rstrip("/")
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)

    def _path(self, content_type: str) -> str:
        key = content_type.strip().lower()
        if key not in CONTENT_PATHS:
            raise ValueError(f"Unsupported content type: {content_type}")
        return CONTENT_PATHS[key]

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def health(self) -> dict[str, Any]:
        try:
            r = await self.client.get(f"{self.cms_base_url}/_health", headers=self._headers())
            return {"ok": r.status_code < 500, "status_code": r.status_code}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def list_content_types(self) -> list[dict[str, Any]]:
        """Static catalog of Phase-A content-types (Strapi has no public /content-types list by default)."""
        return [
            {"name": "page", "path": "/api/pages", "display_name": "صفحه"},
            {"name": "blog-post", "path": "/api/blog-posts", "display_name": "پست وبلاگ"},
            {"name": "category", "path": "/api/categories", "display_name": "دسته"},
            {"name": "tag", "path": "/api/tags", "display_name": "برچسب"},
        ]

    async def get_content_items(
        self, content_type: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        path = self._path(content_type)
        r = await self.client.get(
            f"{self.cms_base_url}/api/{path}",
            headers=self._headers(),
            params=params or {},
        )
        r.raise_for_status()
        return r.json()

    async def get_content_item(self, content_type: str, item_id: int) -> dict[str, Any]:
        path = self._path(content_type)
        r = await self.client.get(
            f"{self.cms_base_url}/api/{path}/{item_id}",
            headers=self._headers(),
        )
        r.raise_for_status()
        return r.json()

    async def create_content_item(self, content_type: str, data: dict[str, Any]) -> dict[str, Any]:
        path = self._path(content_type)
        payload = data if "data" in data else {"data": data}
        r = await self.client.post(
            f"{self.cms_base_url}/api/{path}",
            headers={**self._headers(), "Content-Type": "application/json"},
            json=payload,
        )
        r.raise_for_status()
        return r.json()

    async def update_content_item(
        self, content_type: str, item_id: int, data: dict[str, Any]
    ) -> dict[str, Any]:
        path = self._path(content_type)
        payload = data if "data" in data else {"data": data}
        r = await self.client.put(
            f"{self.cms_base_url}/api/{path}/{item_id}",
            headers={**self._headers(), "Content-Type": "application/json"},
            json=payload,
        )
        r.raise_for_status()
        return r.json()

    async def delete_content_item(self, content_type: str, item_id: int) -> bool:
        path = self._path(content_type)
        r = await self.client.delete(
            f"{self.cms_base_url}/api/{path}/{item_id}",
            headers=self._headers(),
        )
        r.raise_for_status()
        return True

    async def close(self) -> None:
        await self.client.aclose()


_cms_service: CMSIntegrationService | None = None


def init_cms_service_from_env() -> CMSIntegrationService | None:
    global _cms_service
    base = os.getenv("CMS_BASE_URL") or os.getenv("STRAPI_URL") or "http://localhost:1337"
    key = os.getenv("CMS_API_TOKEN") or os.getenv("STRAPI_TOKEN")
    _cms_service = CMSIntegrationService(cms_base_url=base, api_key=key)
    return _cms_service


def get_cms_service() -> CMSIntegrationService | None:
    global _cms_service
    if _cms_service is None:
        return init_cms_service_from_env()
    return _cms_service


def init_cms_service(base_url: str, api_key: str | None = None) -> CMSIntegrationService:
    global _cms_service
    _cms_service = CMSIntegrationService(cms_base_url=base_url, api_key=api_key)
    return _cms_service
