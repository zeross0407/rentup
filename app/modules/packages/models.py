from typing import Optional

from pydantic import Field

from app.models.base import BaseDocument


class Package(BaseDocument):
    """Package tier document."""

    name: str = Field(..., max_length=100)
    tier: str = Field(..., pattern="^(free|silver|gold|diamond)$")
    price_per_day: int = Field(default=0, ge=0)
    package_score: int = Field(default=0)
    free_boosts: int = Field(default=0, ge=0)
    extra_boost_price: int = Field(default=0, ge=0)
    max_posts_per_day: int = Field(default=1, ge=1)
    display_tag: Optional[str] = None
    duration_days: int = Field(default=7, ge=1)
    is_active: bool = Field(default=True)

    class Settings:
        name = "packages"
        indexes = [
            "tier",
            "is_active",
        ]
