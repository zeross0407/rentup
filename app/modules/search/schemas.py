from typing import List, Optional

from pydantic import BaseModel, Field


# ──── Request Schemas ────


class SearchQuery(BaseModel):
    """Search filters for property listings."""
    province: Optional[str] = None
    district: Optional[str] = None
    property_type: Optional[str] = Field(
        None, pattern="^(room|apartment|house|studio)$"
    )
    min_price: Optional[int] = Field(None, ge=0)
    max_price: Optional[int] = Field(None, ge=0)
    min_area: Optional[float] = Field(None, ge=0)
    max_area: Optional[float] = Field(None, ge=0)
    bedrooms: Optional[int] = Field(None, ge=0)
    bathrooms: Optional[int] = Field(None, ge=0)
    amenities: Optional[List[str]] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=50)


class MapSearchQuery(BaseModel):
    """Geo search: find properties in radius."""
    longitude: float
    latitude: float
    radius_km: float = Field(default=5.0, gt=0, le=50)
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    property_type: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=50)


class AIMatchRequest(BaseModel):
    """AI matching request: describe your ideal room."""
    description: str = Field(..., min_length=10, max_length=1000)
    province: Optional[str] = None
    max_price: Optional[int] = None
    limit: int = Field(default=30, ge=1, le=50)


# ──── Response Schemas ────


class AIMatchResult(BaseModel):
    """Single AI match result with match percentage."""
    property_id: str
    title: str
    price: int
    match_percentage: float = Field(..., ge=0, le=100)
    structured_score: float
    semantic_score: float
