from datetime import datetime

from beanie import Indexed, PydanticObjectId
from pydantic import Field

from app.models.base import TimestampDocument


class ViewHistory(TimestampDocument):
    """User property view history entry."""

    user_id: Indexed(PydanticObjectId)
    property_id: Indexed(PydanticObjectId)
    viewed_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "view_history"
        indexes = [
            [("user_id", 1), ("viewed_at", -1)],
            "property_id",
            [("user_id", 1), ("property_id", 1)],
        ]
