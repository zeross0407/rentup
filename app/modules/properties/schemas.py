from datetime import datetime
from typing import Dict, List, Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, Field


# ──── Embedded Schemas ────


class ServiceFeesSchema(BaseModel):
    electricity: int = 0
    water: int = 0
    internet: Optional[int] = None
    parking: Optional[int] = None
    other: List[Dict[str, object]] = Field(default_factory=list)


class RoomsSchema(BaseModel):
    bedroom: int = 1
    bathroom: int = 1
    kitchen: int = 0


class AddressSchema(BaseModel):
    province: str
    district: str
    ward: str
    street: str
    full_address: str


class GeoLocationSchema(BaseModel):
    type: str = "Point"
    coordinates: List[float]  # [longitude, latitude]


class MetricsSchema(BaseModel):
    views: int = 0
    phone_clicks: int = 0
    saves: int = 0
    shares: int = 0


class ActivePackageSchema(BaseModel):
    package_id: PydanticObjectId
    tier: str
    package_score: int
    boosts_remaining: int
    started_at: datetime
    expires_at: datetime


# ──── Request Schemas ────


class PropertyCreate(BaseModel):
    """Create a new property listing."""
    title: str = Field(..., min_length=5, max_length=500)
    description: str = Field(default="")
    property_type: str = Field(
        default="room",
        pattern="^(room|apartment|house|studio)$",
    )
    price: int = Field(..., gt=0)
    service_fees: ServiceFeesSchema = Field(default_factory=ServiceFeesSchema)
    area: float = Field(..., gt=0)
    rooms: RoomsSchema = Field(default_factory=RoomsSchema)
    amenities: List[str] = Field(default_factory=list)
    images: List[str] = Field(..., min_length=3)
    videos: List[str] = Field(default_factory=list)
    address: AddressSchema
    location: GeoLocationSchema


class PropertyUpdate(BaseModel):
    """Update an existing property listing."""
    title: Optional[str] = Field(None, min_length=5, max_length=500)
    description: Optional[str] = None
    property_type: Optional[str] = Field(
        None, pattern="^(room|apartment|house|studio)$"
    )
    price: Optional[int] = Field(None, gt=0)
    service_fees: Optional[ServiceFeesSchema] = None
    area: Optional[float] = Field(None, gt=0)
    rooms: Optional[RoomsSchema] = None
    amenities: Optional[List[str]] = None
    images: Optional[List[str]] = None
    videos: Optional[List[str]] = None
    address: Optional[AddressSchema] = None
    location: Optional[GeoLocationSchema] = None


class PropertyStatusUpdate(BaseModel):
    """Admin: change property status (approve/reject)."""
    status: str = Field(
        ..., pattern="^(active|hidden|rejected)$"
    )
    reject_reason: Optional[str] = None


class GenerateDescriptionRequest(BaseModel):
    """Request AI to generate property description."""
    keywords: List[str] = Field(default_factory=list)
    tone: str = Field(default="professional", pattern="^(professional|friendly|luxury)$")


# ──── Response Schemas ────


class PropertyResponse(BaseModel):
    """Property listing response."""
    id: PydanticObjectId = Field(..., alias="_id")
    host_id: PydanticObjectId
    title: str
    description: str
    property_type: str
    price: int
    service_fees: ServiceFeesSchema
    area: float
    rooms: RoomsSchema
    amenities: List[str]
    images: List[str]
    videos: List[str]
    address: AddressSchema
    location: GeoLocationSchema
    status: str
    reject_reason: Optional[str] = None
    active_package: Optional[ActivePackageSchema] = None
    metrics: MetricsSchema
    ranking_score: float
    final_score: float
    published_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class PropertyListResponse(BaseModel):
    """Simplified property for list views."""
    id: PydanticObjectId = Field(..., alias="_id")
    title: str
    property_type: str
    price: int
    area: float
    rooms: RoomsSchema
    images: List[str]
    address: AddressSchema
    status: str
    active_package: Optional[ActivePackageSchema] = None
    metrics: MetricsSchema
    final_score: float
    created_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}
