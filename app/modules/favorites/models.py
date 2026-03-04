from datetime import datetime

from beanie import Indexed, PydanticObjectId
from pydantic import Field

from app.models.base import TimestampDocument


class Favorite(TimestampDocument):
    """User favorite/saved property."""

    user_id: Indexed(PydanticObjectId)
    property_id: PydanticObjectId

    class Settings:
        name = "favorites"
        indexes = [
            [("user_id", 1), ("property_id", 1)],  # unique compound
            [("user_id", 1), ("created_at", -1)],
        ]
