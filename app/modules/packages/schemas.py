from datetime import datetime
from typing import Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, Field


# ──── Response Schemas ────


class PackageResponse(BaseModel):
    """Package tier response."""
    id: PydanticObjectId = Field(..., alias="_id")
    name: str
    tier: str
    price_per_day: int
    package_score: int
    free_boosts: int
    extra_boost_price: int
    max_posts_per_day: int
    display_tag: Optional[str] = None
    duration_days: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}
