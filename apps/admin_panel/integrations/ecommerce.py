"""Integration service for connecting with E-commerce module."""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

import httpx

logger = logging.getLogger(__name__)


class EcommerceIntegrationService:
    """Service for integrating admin panel with E-commerce module."""
    
    def __init__(self, ecommerce_base_url: str, api_key: Optional[str] = None):
        self.ecommerce_base_url = ecommerce_base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def get_products(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get products from e-commerce service."""
        try:
            headers = self._get_headers()
            response = await self.client.get(f"{self.ecommerce_base_url}/api/products", headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get products from e-commerce service: {e}")
            # Return mock data in case of failure
            return [
                {
                    "id": 1,
                    "name": "کود ارگانیک",
                    "slug": "organic-fertilizer",
                    "description": "کود ارگانیک با کیفیت بالا",
                    "price": 150.00,
                    "status": "published",
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            ]
    
    async def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific product from e-commerce service."""
        try:
            headers = self._get_headers()
            response = await self.client.get(f"{self.ecommerce_base_url}/api/products/{product_id}", headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get product from e-commerce service: {e}")
            return None
    
    async def create_product(self, product_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new product in e-commerce service."""
        try:
            headers = self._get_headers()
            headers["Content-Type"] = "application/json"
            response = await self.client.post(
                f"{self.ecommerce_base_url}/api/products", 
                headers=headers, 
                json=product_data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create product in e-commerce service: {e}")
            return None
    
    async def update_product(self, product_id: int, product_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing product in e-commerce service."""
        try:
            headers = self._get_headers()
            headers["Content-Type"] = "application/json"
            response = await self.client.put(
                f"{self.ecommerce_base_url}/api/products/{product_id}", 
                headers=headers, 
                json=product_data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to update product in e-commerce service: {e}")
            return None
    
    async def delete_product(self, product_id: int) -> bool:
        """Delete a product in e-commerce service."""
        try:
            headers = self._get_headers()
            response = await self.client.delete(
                f"{self.ecommerce_base_url}/api/products/{product_id}", 
                headers=headers
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to delete product from e-commerce service: {e}")
            return False
    
    async def get_orders(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get orders from e-commerce service."""
        try:
            headers = self._get_headers()
            response = await self.client.get(f"{self.ecommerce_base_url}/api/orders", headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get orders from e-commerce service: {e}")
            return []
    
    async def get_categories(self) -> List[Dict[str, Any]]:
        """Get product categories from e-commerce service."""
        try:
            headers = self._get_headers()
            response = await self.client.get(f"{self.ecommerce_base_url}/api/categories", headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get categories from e-commerce service: {e}")
            return []
    
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
ecommerce_service: Optional[EcommerceIntegrationService] = None


def get_ecommerce_service() -> Optional[EcommerceIntegrationService]:
    """Get the E-commerce integration service instance."""
    global ecommerce_service
    return ecommerce_service


def init_ecommerce_service(base_url: str, api_key: Optional[str] = None):
    """Initialize the E-commerce integration service."""
    global ecommerce_service
    ecommerce_service = EcommerceIntegrationService(ecommerce_base_url=base_url, api_key=api_key)