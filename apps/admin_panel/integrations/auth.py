"""Integration service for connecting with Authentication module."""

import logging
from typing import Any, Dict, Optional
from datetime import datetime

import httpx

logger = logging.getLogger(__name__)


class AuthIntegrationService:
    """Service for integrating admin panel with Authentication module."""
    
    def __init__(self, auth_base_url: str, api_key: Optional[str] = None):
        self.auth_base_url = auth_base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user profile from authentication service."""
        try:
            headers = self._get_headers()
            response = await self.client.get(f"{self.auth_base_url}/api/users/{user_id}", headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get user profile from auth service: {e}")
            return None
    
    async def update_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user profile in authentication service."""
        try:
            headers = self._get_headers()
            headers["Content-Type"] = "application/json"
            response = await self.client.put(
                f"{self.auth_base_url}/api/users/{user_id}", 
                headers=headers, 
                json=profile_data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to update user profile in auth service: {e}")
            return None
    
    async def get_user_permissions(self, user_id: int) -> list[str]:
        """Get user permissions from authentication service."""
        try:
            headers = self._get_headers()
            response = await self.client.get(f"{self.auth_base_url}/api/users/{user_id}/permissions", headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get user permissions from auth service: {e}")
            return []
    
    async def assign_user_role(self, user_id: int, role: str) -> bool:
        """Assign a role to a user in authentication service."""
        try:
            headers = self._get_headers()
            headers["Content-Type"] = "application/json"
            response = await self.client.post(
                f"{self.auth_base_url}/api/users/{user_id}/roles", 
                headers=headers, 
                json={"role": role}
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to assign user role in auth service: {e}")
            return False
    
    async def revoke_user_role(self, user_id: int, role: str) -> bool:
        """Revoke a role from a user in authentication service."""
        try:
            headers = self._get_headers()
            response = await self.client.delete(
                f"{self.auth_base_url}/api/users/{user_id}/roles/{role}", 
                headers=headers
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to revoke user role in auth service: {e}")
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
auth_service: Optional[AuthIntegrationService] = None


def get_auth_service() -> Optional[AuthIntegrationService]:
    """Get the Auth integration service instance."""
    global auth_service
    return auth_service


def init_auth_service(base_url: str, api_key: Optional[str] = None):
    """Initialize the Auth integration service."""
    global auth_service
    auth_service = AuthIntegrationService(auth_base_url=base_url, api_key=api_key)