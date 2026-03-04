from datetime import datetime
from typing import Dict, List, Optional

from beanie import Indexed, PydanticObjectId
from pydantic import BaseModel, Field

from app.models.base import BaseDocument


# ──── Embedded Sub-Models (NOT separate collections) ────


class ServiceFees(BaseModel):
    """Embedded service fees."""
    electricity: int = 0
    water: int = 0
    internet: Optional[int] = None
    parking: Optional[int] = None
    other: List[Dict[str, object]] = Field(default_factory=list)


class Rooms(BaseModel):
    """Embedded room counts."""
    bedroom: int = 1
    bathroom: int = 1
    kitchen: int = 0


class Address(BaseModel):
    """Embedded address."""
    province: str
    district: str
    ward: str
    street: str
    full_address: str


class GeoLocation(BaseModel):
    """GeoJSON Point for MongoDB 2dsphere queries."""
    type: str = Field(default="Point")
    coordinates: List[float]  # [longitude, latitude]


class ActivePackage(BaseModel):
    """Embedded snapshot of the active package at time of purchase."""
    package_id: PydanticObjectId
    tier: str = Field(..., pattern="^(free|silver|gold|diamond)$")
    package_score: int = 0
    boosts_remaining: int = 0
    started_at: datetime
    expires_at: datetime


class Metrics(BaseModel):
    """Embedded interaction metrics."""
    views: int = 0
    phone_clicks: int = 0
    saves: int = 0
    shares: int = 0


# ──── Property Document ────


class Property(BaseDocument):
    """Property listing document."""

    host_id: Indexed(PydanticObjectId)
    title: str = Field(..., max_length=500)
    description: str = Field(default="")
    property_type: str = Field(
        default="room",
        pattern="^(room|apartment|house|studio)$",
    )

    # Pricing
    price: int = Field(..., gt=0)
    service_fees: ServiceFees = Field(default_factory=ServiceFees)

    # Rooms & amenities
    area: float = Field(..., gt=0)
    rooms: Rooms = Field(default_factory=Rooms)
    amenities: List[str] = Field(default_factory=list)

    # Media
    images: List[str] = Field(default_factory=list)
    videos: List[str] = Field(default_factory=list)

    # Location
    address: Address
    location: GeoLocation

    # Status
    status: str = Field(
        default="draft",
        pattern="^(draft|pending|active|hidden|expired|rejected)$",
    )
    reject_reason: Optional[str] = None

    # Package
    active_package: Optional[ActivePackage] = None

    # Metrics & ranking
    metrics: Metrics = Field(default_factory=Metrics)
    ranking_score: float = Field(default=0.0)
    final_score: float = Field(default=0.0)

    # AI Vector embedding
    embedding: Optional[List[float]] = None

    published_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    class Settings:
        name = "properties"
        indexes = [
            "host_id",
            [("status", 1), ("final_score", -1)],
            [("location", "2dsphere")],
            "price",
            "property_type",
            [("address.province", 1), ("address.district", 1)],
            [("created_at", -1)],
        ]
