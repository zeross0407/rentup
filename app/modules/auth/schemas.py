from typing import Optional

from pydantic import BaseModel, Field


# ──── Request Schemas ────


class RegisterRequest(BaseModel):
    """Register a new user account."""
    phone: str = Field(..., pattern=r"^(0|\+84)\d{9}$", examples=["0912345678"])
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)


class LoginRequest(BaseModel):
    """Login with phone number and password."""
    phone: str = Field(..., pattern=r"^(0|\+84)\d{9}$", examples=["0912345678"])
    password: str = Field(...)


class RefreshTokenRequest(BaseModel):
    """Refresh access token."""
    refresh_token: str


# ──── Response Schemas ────


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
