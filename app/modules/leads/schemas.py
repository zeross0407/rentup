from datetime import datetime
from typing import Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, Field


# ──── Request Schemas ────


class LeadCreate(BaseModel):
    """Record a tenant action on a property."""
    property_id: PydanticObjectId
    action: str = Field(
        ..., pattern="^(view_detail|click_phone|save|share)$"
    )


# ──── Response Schemas ────


class LeadResponse(BaseModel):
    """Lead entry response."""
    id: PydanticObjectId = Field(..., alias="_id")
    tenant_id: PydanticObjectId
    property_id: PydanticObjectId
    host_id: PydanticObjectId
    action: str
    created_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class LeadStatsResponse(BaseModel):
    """Aggregated lead stats for host dashboard."""
    total_views: int = 0
    total_phone_clicks: int = 0
    total_saves: int = 0
    total_shares: int = 0
    unique_tenants: int = 0
