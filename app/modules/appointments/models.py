from datetime import datetime
from typing import Optional

from beanie import Indexed, PydanticObjectId
from pydantic import Field

from app.models.base import BaseDocument


class Appointment(BaseDocument):
    """Appointment for property viewing."""

    tenant_id: Indexed(PydanticObjectId)
    host_id: Indexed(PydanticObjectId)
    property_id: Indexed(PydanticObjectId)
    proposed_time: datetime
    alternative_time: Optional[datetime] = None
    note: Optional[str] = Field(None, max_length=500)
    status: str = Field(
        default="pending",
        pattern="^(pending|confirmed|rejected|cancelled|rescheduled)$",
    )

    class Settings:
        name = "appointments"
        indexes = [
            [("tenant_id", 1), ("status", 1)],
            [("host_id", 1), ("status", 1)],
            "property_id",
            "proposed_time",
        ]
