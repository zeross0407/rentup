from datetime import datetime
from typing import Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, Field


# ──── Request Schemas ────


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: str = Field(..., max_length=255, examples=["user@example.com"])
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)


class UserLogin(BaseModel):
    """Schema for user login."""

    email: str = Field(..., examples=["user@example.com"])
    password: str = Field(...)


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    full_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)


# ──── Response Schemas ────


class UserResponse(BaseModel):
    """Schema for user data in responses."""

    id: PydanticObjectId = Field(..., alias="_id")
    email: str
    full_name: str
    phone: Optional[str] = None
    is_active: bool
    role: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class TokenResponse(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str = "bearer"


class LoginResponse(BaseModel):
    """Schema for login response with token and user data."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
