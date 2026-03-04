from typing import List

from beanie import PydanticObjectId
from fastapi import APIRouter, Query

from app.modules.search.schemas import (
    AIMatchRequest,
    AIMatchResult,
    MapSearchQuery,
    SearchQuery,
)
from app.modules.properties.models import Property
from app.modules.properties.schemas import PropertyListResponse
from app.schemas.base import PaginatedResponse, ResponseSchema

router = APIRouter(prefix="/search", tags=["Search"])


@router.get(
    "",
    response_model=PaginatedResponse[PropertyListResponse],
    summary="Search properties with filters",
)
async def search_properties(
    province: str = None,
    district: str = None,
    property_type: str = None,
    min_price: int = None,
    max_price: int = None,
    min_area: float = None,
    max_area: float = None,
    bedrooms: int = None,
    bathrooms: int = None,
    amenities: str = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    """Search active properties with basic filters."""
    filters = {"status": "active"}

    if province:
        filters["address.province"] = province
    if district:
        filters["address.district"] = district
    if property_type:
        filters["property_type"] = property_type
    if bedrooms is not None:
        filters["rooms.bedroom"] = {"$gte": bedrooms}
    if bathrooms is not None:
        filters["rooms.bathroom"] = {"$gte": bathrooms}

    # Price range
    if min_price is not None or max_price is not None:
        price_filter = {}
        if min_price is not None:
            price_filter["$gte"] = min_price
        if max_price is not None:
            price_filter["$lte"] = max_price
        filters["price"] = price_filter

    # Area range
    if min_area is not None or max_area is not None:
        area_filter = {}
        if min_area is not None:
            area_filter["$gte"] = min_area
        if max_area is not None:
            area_filter["$lte"] = max_area
        filters["area"] = area_filter

    # Amenities (must contain all listed)
    if amenities:
        amenity_list = [a.strip() for a in amenities.split(",")]
        filters["amenities"] = {"$all": amenity_list}

    skip = (page - 1) * page_size
    collection = Property.get_motor_collection()
    total = await collection.count_documents(filters)
    cursor = (
        collection
        .find(filters)
        .sort("final_score", -1)
        .skip(skip)
        .limit(page_size)
    )
    items_raw = await cursor.to_list(length=page_size)
    items = [PropertyListResponse(**item) for item in items_raw]

    return PaginatedResponse.create(
        items=items, total=total, page=page, page_size=page_size,
    )


@router.get(
    "/map",
    response_model=PaginatedResponse[PropertyListResponse],
    summary="Search properties on map (geo radius)",
)
async def search_map(
    longitude: float = Query(...),
    latitude: float = Query(...),
    radius_km: float = Query(5.0, gt=0, le=50),
    min_price: int = None,
    max_price: int = None,
    property_type: str = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    """Find properties within a radius using MongoDB $near (2dsphere)."""
    filters = {
        "status": "active",
        "location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude],
                },
                "$maxDistance": radius_km * 1000,  # meters
            }
        },
    }

    if property_type:
        filters["property_type"] = property_type
    if min_price is not None or max_price is not None:
        price_filter = {}
        if min_price is not None:
            price_filter["$gte"] = min_price
        if max_price is not None:
            price_filter["$lte"] = max_price
        filters["price"] = price_filter

    skip = (page - 1) * page_size
    collection = Property.get_motor_collection()
    total = await collection.count_documents(filters)
    cursor = collection.find(filters).skip(skip).limit(page_size)
    items_raw = await cursor.to_list(length=page_size)
    items = [PropertyListResponse(**item) for item in items_raw]

    return PaginatedResponse.create(
        items=items, total=total, page=page, page_size=page_size,
    )


@router.post(
    "/ai-match",
    response_model=ResponseSchema[List[AIMatchResult]],
    summary="AI matching: find best-fit properties",
)
async def ai_match(data: AIMatchRequest):
    """
    AI-powered property matching.
    final_score = (structured_score * 0.6) + (semantic_score * 0.4)

    Returns top N properties with match percentage.
    """
    # TODO: Implement AI matching with vector embeddings
    # 1. Generate embedding from data.description
    # 2. Vector search in MongoDB Atlas
    # 3. Combine structured + semantic scores
    return ResponseSchema(
        message="AI matching is not yet implemented",
        data=[],
    )
