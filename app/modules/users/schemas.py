from datetime import datetime
from typing import Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, Field


# ──── Request Schemas ────


class UserUpdate(BaseModel):
    """Update user profile."""
    full_name: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = None


class UpgradeHostRequest(BaseModel):
    """Submit identity info to upgrade to Host role."""
    id_number: str = Field(..., min_length=9, max_length=12)
    issued_date: datetime
    issued_place: str = Field(..., max_length=255)
    front_image_url: str
    back_image_url: str


# ──── Response Schemas ────


class UserIdentityResponse(BaseModel):
    """Identity verification response data."""
    id_number: str
    issued_date: datetime
    issued_place: str
    verified: bool
    verified_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    """User profile response."""
    id: PydanticObjectId = Field(..., alias="_id")
    phone: str
    role: str
    full_name: str
    avatar_url: Optional[str] = None
    email: Optional[str] = None
    identity: Optional[UserIdentityResponse] = None
    is_active: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}
