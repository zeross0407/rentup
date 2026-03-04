from beanie import Indexed, PydanticObjectId
from pydantic import Field

from app.models.base import TimestampDocument


class Lead(TimestampDocument):
    """Lead tracking - records tenant actions on host properties."""

    tenant_id: Indexed(PydanticObjectId)
    property_id: Indexed(PydanticObjectId)
    host_id: Indexed(PydanticObjectId)
    action: str = Field(
        ..., pattern="^(view_detail|click_phone|save|share)$"
    )

    class Settings:
        name = "leads"
        indexes = [
            [("host_id", 1), ("created_at", -1)],
            [("property_id", 1), ("action", 1)],
            "tenant_id",
        ]
