"""
notification_schema.py

Pydantic schemas for Aladdin notifications.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from datetime import datetime

from pydantic import BaseModel


class NotificationResponseSchema(BaseModel):
    """
    Schema used when returning a notification through the API.
    """

    id: int
    user_id: int
    notification_type: str
    title: str
    message: str
    trade_id: str | None
    priority: str
    is_read: int
    created_at: datetime