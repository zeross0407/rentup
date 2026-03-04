from datetime import datetime
from typing import List, Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, Field


# ──── Request Schemas ────


class ReportCreate(BaseModel):
    """Report a property violation."""
    property_id: PydanticObjectId
    reason: str = Field(
        ..., pattern="^(scam|duplicate|wrong_info|inappropriate|other)$"
    )
    description: Optional[str] = Field(None, max_length=1000)
    attachments: List[str] = Field(default_factory=list)


class ReportAdminUpdate(BaseModel):
    """Admin updates report status."""
    status: str = Field(..., pattern="^(reviewed|resolved)$")
    admin_note: Optional[str] = None


# ──── Response Schemas ────


class ReportResponse(BaseModel):
    """Report response."""
    id: PydanticObjectId = Field(..., alias="_id")
    reporter_id: PydanticObjectId
    property_id: PydanticObjectId
    reason: str
    description: Optional[str] = None
    attachments: List[str]
    status: str
    admin_note: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}
