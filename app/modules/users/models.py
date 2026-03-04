from datetime import datetime
from typing import Optional

from beanie import Indexed
from pydantic import BaseModel, Field

from app.models.base import BaseDocument


# ──── Embedded Sub-Models ────


class UserIdentity(BaseModel):
    """Embedded identity verification info."""
    id_number: str
    issued_date: datetime
    issued_place: str
    front_image_url: str
    back_image_url: str
    verified: bool = False
    verified_at: Optional[datetime] = None


# ──── User Document ────


class User(BaseDocument):
    """User document for authentication and profile."""

    phone: Indexed(str, unique=True)
    hashed_password: str = Field(..., max_length=255)
    role: str = Field(default="tenant", pattern="^(tenant|host|admin)$")
    full_name: str = Field(..., max_length=255)
    avatar_url: Optional[str] = None
    email: Optional[str] = None

    # Embedded: Identity verification (host upgrade)
    identity: Optional[UserIdentity] = None

    is_active: bool = Field(default=True)
    last_login_at: Optional[datetime] = None

    class Settings:
        name = "users"
        indexes = [
            "phone",
            "role",
            "identity.verified",
        ]
