from datetime import datetime
from typing import Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, Field


# ──── Request Schemas ────


class AppointmentCreate(BaseModel):
    """Tenant requests a viewing appointment."""
    property_id: PydanticObjectId
    proposed_time: datetime
    note: Optional[str] = Field(None, max_length=500)


class AppointmentReschedule(BaseModel):
    """Host proposes an alternative time."""
    alternative_time: datetime


# ──── Response Schemas ────


class AppointmentResponse(BaseModel):
    """Appointment response."""
    id: PydanticObjectId = Field(..., alias="_id")
    tenant_id: PydanticObjectId
    host_id: PydanticObjectId
    property_id: PydanticObjectId
    proposed_time: datetime
    alternative_time: Optional[datetime] = None
    note: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}
