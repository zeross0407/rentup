from typing import Optional

from beanie import Indexed, PydanticObjectId
from pydantic import Field

from app.models.base import TimestampDocument


class Notification(TimestampDocument):
    """User notification."""

    user_id: Indexed(PydanticObjectId)
    type: str = Field(
        ...,
        pattern="^(appointment|payment|property_status|chat|system)$",
    )
    title: str = Field(..., max_length=255)
    body: str = Field(..., max_length=500)
    data: Optional[dict] = None
    is_read: bool = Field(default=False)

    class Settings:
        name = "notifications"
        indexes = [
            [("user_id", 1), ("is_read", 1), ("created_at", -1)],
        ]
