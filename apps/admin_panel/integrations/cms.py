"""Integration service for connecting with CMS module."""

import logging
from typing import Any, Dict, Optional
from datetime import datetime

import httpx

logger = logging.getLogger(__name__)


class CMSIntegrationService:
    """Service for integrating admin panel with CMS module."""
    
    def __init__(self, cms_base_url: str, api_key: Optional[str] = None):
        self.cms_base_url = cms_base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def get_content_types(self) -> list[Dict[str, Any]]:
        """Get all available content types from CMS."""
        try:
            headers = self._get_headers()
            response = await self.client.get(f"{self.cms_base_url}/api/content-types", headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get content types from CMS: {e}")
            # Return mock data in case of failure
            return [
                {
                    "name": "page",
                    "display_name": "صفحه",
                    "description": "صفحات محتوایی سایت",
                    "fields": [
                        {"name": "title", "type": "string", "required": True},
                        {"name": "slug", "type": "string", "required": True},
                        {"name": "content", "type": "richtext", "required": True},
                        {"name": "status", "type": "enumeration", "options": ["draft", "published", "archived"]}
                    ],
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
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
                        {"name": "status", "type": "enumeration", "options": ["draft", "published", "archived"]}
                    ],
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            ]
    
    async def get_content_items(self, content_type: str, params: Optional[Dict[str, Any]] = None) -> list[Dict[str, Any]]:
        """Get content items of a specific type from CMS."""
        try:
            headers = self._get_headers()
            url = f"{self.cms_base_url}/api/{content_type}s"  # Assuming plural form
            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get content items from CMS: {e}")
            # Return mock data in case of failure
            return []
    
    async def get_content_item(self, content_type: str, item_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific content item from CMS."""
        try:
            headers = self._get_headers()
            url = f"{self.cms_base_url}/api/{content_type}s/{item_id}"
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get content item from CMS: {e}")
            return None
    
    async def create_content_item(self, content_type: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new content item in CMS."""
        try:
            headers = self._get_headers()
            headers["Content-Type"] = "application/json"
            url = f"{self.cms_base_url}/api/{content_type}s"
            response = await self.client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create content item in CMS: {e}")
            return None
    
    async def update_content_item(self, content_type: str, item_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing content item in CMS."""
        try:
            headers = self._get_headers()
            headers["Content-Type"] = "application/json"
            url = f"{self.cms_base_url}/api/{content_type}s/{item_id}"
            response = await self.client.put(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to update content item in CMS: {e}")
            return None
    
    async def delete_content_item(self, content_type: str, item_id: int) -> bool:
        """Delete a content item in CMS."""
        try:
            headers = self._get_headers()
            url = f"{self.cms_base_url}/api/{content_type}s/{item_id}"
            response = await self.client.delete(url, headers=headers)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to delete content item from CMS: {e}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get default headers for API requests."""
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global instance - in a real application, this would be managed differently
cms_service: Optional[CMSIntegrationService] = None


def get_cms_service() -> Optional[CMSIntegrationService]:
    """Get the CMS integration service instance."""
    global cms_service
    return cms_service


def init_cms_service(base_url: str, api_key: Optional[str] = None):
    """Initialize the CMS integration service."""
    global cms_service
    cms_service = CMSIntegrationService(cms_base_url=base_url, api_key=api_key)