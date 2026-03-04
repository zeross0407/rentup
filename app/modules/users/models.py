from typing import Optional

from pydantic import Field

from app.models.base import BaseDocument


class User(BaseDocument):
    """User document for authentication and profile."""

    email: str = Field(..., max_length=255)
    hashed_password: str = Field(..., max_length=255)
    full_name: str = Field(..., max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    is_active: bool = Field(default=True)
    role: str = Field(default="user", max_length=50)

    class Settings:
        name = "users"  # MongoDB collection name
        indexes = [
            "email",  # Create index on email field
        ]
