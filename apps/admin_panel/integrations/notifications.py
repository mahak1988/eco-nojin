"""Notification service for admin panel."""

import logging
from datetime import datetime
from enum import Enum
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Types of notifications."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class NotificationPriority(Enum):
    """Priority levels for notifications."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationService:
    """Service for managing notifications in the admin panel."""

    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)

        # In-memory storage for notifications (in production, this would be a database)
        self.notifications: list[dict[str, Any]] = []

    async def send_notification(
        self,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        recipients: list[str] | None = None,
        data: dict[str, Any] | None = None,
    ) -> bool:
        """Send a notification to users."""
        try:
            notification = {
                "id": len(self.notifications) + 1,
                "title": title,
                "message": message,
                "type": notification_type.value,
                "priority": priority.value,
                "recipients": recipients or [],
                "data": data or {},
                "timestamp": datetime.utcnow().isoformat(),
                "read": False,
            }

            self.notifications.append(notification)

            # Keep only the last 1000 notifications
            if len(self.notifications) > 1000:
                self.notifications = self.notifications[-1000:]

            # If we have a base URL, send to external notification service
            if self.base_url:
                await self._send_external_notification(notification)

            logger.info(f"Notification sent: {title}")
            return True
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False

    async def get_notifications(
        self, user_id: int | None = None, unread_only: bool = False, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Get notifications, optionally filtered by user and read status."""
        try:
            notifications = self.notifications.copy()

            # Filter by user if specified
            if user_id:
                notifications = [
                    n
                    for n in notifications
                    if not n["recipients"] or str(user_id) in n["recipients"]
                ]

            # Filter by read status if requested
            if unread_only:
                notifications = [n for n in notifications if not n["read"]]

            # Sort by timestamp (newest first)
            notifications.sort(key=lambda x: x["timestamp"], reverse=True)

            # Limit results
            return notifications[:limit]
        except Exception as e:
            logger.error(f"Failed to get notifications: {e}")
            return []

    async def mark_as_read(self, notification_ids: list[int], user_id: int | None = None) -> bool:
        """Mark notifications as read."""
        try:
            updated_count = 0
            for notification in self.notifications:
                if notification["id"] in notification_ids:
                    # If user-specific notifications, check if user is recipient
                    if not user_id or (
                        notification["recipients"] and str(user_id) in notification["recipients"]
                    ):
                        notification["read"] = True
                        updated_count += 1

            logger.info(f"Marked {updated_count} notifications as read")
            return True
        except Exception as e:
            logger.error(f"Failed to mark notifications as read: {e}")
            return False

    async def delete_notification(self, notification_id: int) -> bool:
        """Delete a notification."""
        try:
            original_count = len(self.notifications)
            self.notifications = [n for n in self.notifications if n["id"] != notification_id]
            deleted_count = original_count - len(self.notifications)

            logger.info(f"Deleted notification ID: {notification_id}")
            return deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete notification: {e}")
            return False

    async def _send_external_notification(self, notification: dict[str, Any]) -> bool:
        """Send notification to external service."""
        try:
            if not self.base_url:
                return False

            headers = self._get_headers()
            headers["Content-Type"] = "application/json"

            response = await self.client.post(
                f"{self.base_url}/api/notifications", headers=headers, json=notification
            )
            response.raise_for_status()

            return True
        except Exception as e:
            logger.error(f"Failed to send external notification: {e}")
            return False

    def _get_headers(self) -> dict[str, str]:
        """Get default headers for API requests."""
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global instance - in a real application, this would be managed differently
notification_service: NotificationService | None = None


def get_notification_service() -> NotificationService | None:
    """Get the notification service instance."""
    global notification_service
    return notification_service


def init_notification_service(base_url: str | None = None, api_key: str | None = None):
    """Initialize the notification service."""
    global notification_service
    notification_service = NotificationService(base_url=base_url, api_key=api_key)
