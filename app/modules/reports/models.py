from typing import List, Optional

from beanie import Indexed, PydanticObjectId
from pydantic import Field

from app.models.base import BaseDocument


class Report(BaseDocument):
    """Report a property listing for violations."""

    reporter_id: Indexed(PydanticObjectId)
    property_id: Indexed(PydanticObjectId)
    reason: str = Field(
        ...,
        pattern="^(scam|duplicate|wrong_info|inappropriate|other)$",
    )
    description: Optional[str] = Field(None, max_length=1000)
    attachments: List[str] = Field(default_factory=list)
    status: str = Field(
        default="pending",
        pattern="^(pending|reviewed|resolved)$",
    )
    admin_note: Optional[str] = None

    class Settings:
        name = "reports"
        indexes = [
            [("property_id", 1), ("status", 1)],
            "reporter_id",
            [("status", 1), ("created_at", -1)],
        ]
