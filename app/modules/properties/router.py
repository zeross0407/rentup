from typing import List

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_current_user
from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.modules.properties.models import Property
from app.modules.properties.schemas import (
    GenerateDescriptionRequest,
    PropertyCreate,
    PropertyListResponse,
    PropertyResponse,
    PropertyStatusUpdate,
    PropertyUpdate,
)
from app.modules.users.models import User
from app.schemas.base import PaginatedResponse, ResponseSchema

router = APIRouter(prefix="/properties", tags=["Properties"])


@router.post(
    "",
    response_model=ResponseSchema[PropertyResponse],
    status_code=201,
    summary="Create a property listing",
)
async def create_property(
    data: PropertyCreate,
    current_user: User = Depends(get_current_user),
):
    """Create a new property listing. Host only."""
    if current_user.role not in ("host", "admin"):
        raise ForbiddenException(detail="Only hosts can create listings")

    from app.modules.properties.models import (
        Address, GeoLocation, Rooms, ServiceFees,
    )

    prop = Property(
        host_id=current_user.id,
        title=data.title,
        description=data.description,
        property_type=data.property_type,
        price=data.price,
        service_fees=ServiceFees(**data.service_fees.model_dump()),
        area=data.area,
        rooms=Rooms(**data.rooms.model_dump()),
        amenities=data.amenities,
        images=data.images,
        videos=data.videos,
        address=Address(**data.address.model_dump()),
        location=GeoLocation(**data.location.model_dump()),
        status="draft",
    )
    await prop.insert()
    return ResponseSchema(
        message="Property created as draft",
        data=PropertyResponse.model_validate(prop),
    )


@router.get(
    "",
    response_model=PaginatedResponse[PropertyListResponse],
    summary="List active properties",
)
async def list_properties(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    """List active property listings sorted by final_score."""
    skip = (page - 1) * page_size
    query = Property.find(Property.status == "active")
    total = await query.count()
    items = (
        await query
        .sort(-Property.final_score)
        .skip(skip)
        .limit(page_size)
        .to_list()
    )
    return PaginatedResponse.create(
        items=[PropertyListResponse.model_validate(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/my",
    response_model=ResponseSchema[List[PropertyListResponse]],
    summary="List my properties (Host)",
)
async def my_properties(
    current_user: User = Depends(get_current_user),
):
    """List all properties created by the current host."""
    items = (
        await Property.find(Property.host_id == current_user.id)
        .sort(-Property.created_at)
        .to_list()
    )
    return ResponseSchema(
        data=[PropertyListResponse.model_validate(p) for p in items],
    )


@router.get(
    "/{property_id}",
    response_model=ResponseSchema[PropertyResponse],
    summary="Get property detail",
)
async def get_property(property_id: str):
    """Get a single property listing by ID."""
    prop = await Property.get(PydanticObjectId(property_id))
    if not prop:
        raise NotFoundException(detail="Property not found")
    return ResponseSchema(data=PropertyResponse.model_validate(prop))


@router.put(
    "/{property_id}",
    response_model=ResponseSchema[PropertyResponse],
    summary="Update property (Host owner)",
)
async def update_property(
    property_id: str,
    data: PropertyUpdate,
    current_user: User = Depends(get_current_user),
):
    """Update a property listing. Only the owner host can edit."""
    prop = await Property.get(PydanticObjectId(property_id))
    if not prop:
        raise NotFoundException(detail="Property not found")
    if prop.host_id != current_user.id and current_user.role != "admin":
        raise ForbiddenException()

    update_data = data.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(prop, key, value)
    await prop.save_with_timestamp()
    return ResponseSchema(
        message="Property updated",
        data=PropertyResponse.model_validate(prop),
    )


@router.delete(
    "/{property_id}",
    response_model=ResponseSchema,
    summary="Delete property (Host owner)",
)
async def delete_property(
    property_id: str,
    current_user: User = Depends(get_current_user),
):
    """Delete a property listing. Only the owner host can delete."""
    prop = await Property.get(PydanticObjectId(property_id))
    if not prop:
        raise NotFoundException(detail="Property not found")
    if prop.host_id != current_user.id and current_user.role != "admin":
        raise ForbiddenException()

    await prop.delete()
    return ResponseSchema(message="Property deleted")


@router.patch(
    "/{property_id}/status",
    response_model=ResponseSchema[PropertyResponse],
    summary="Change property status (Admin)",
)
async def update_status(
    property_id: str,
    data: PropertyStatusUpdate,
    current_user: User = Depends(get_current_user),
):
    """Admin: approve, reject, or hide a property listing."""
    if current_user.role != "admin":
        raise ForbiddenException(detail="Admin only")

    prop = await Property.get(PydanticObjectId(property_id))
    if not prop:
        raise NotFoundException(detail="Property not found")

    prop.status = data.status
    prop.reject_reason = data.reject_reason
    await prop.save_with_timestamp()
    return ResponseSchema(
        message=f"Property status changed to {data.status}",
        data=PropertyResponse.model_validate(prop),
    )


@router.post(
    "/{property_id}/boost",
    response_model=ResponseSchema[PropertyResponse],
    summary="Boost property (Host)",
)
async def boost_property(
    property_id: str,
    current_user: User = Depends(get_current_user),
):
    """Boost a property listing to the top. Consumes a boost from active package."""
    prop = await Property.get(PydanticObjectId(property_id))
    if not prop:
        raise NotFoundException(detail="Property not found")
    if prop.host_id != current_user.id:
        raise ForbiddenException()
    if not prop.active_package or prop.active_package.boosts_remaining <= 0:
        raise BadRequestException(detail="No boosts remaining")

    prop.active_package.boosts_remaining -= 1
    from datetime import datetime
    prop.published_at = datetime.utcnow()
    await prop.save_with_timestamp()
    return ResponseSchema(
        message="Property boosted",
        data=PropertyResponse.model_validate(prop),
    )


@router.post(
    "/{property_id}/generate-description",
    response_model=ResponseSchema,
    summary="AI generate property description",
)
async def generate_description(
    property_id: str,
    data: GenerateDescriptionRequest,
    current_user: User = Depends(get_current_user),
):
    """Use AI to generate a property description based on keywords and tone."""
    # TODO: Integrate with AI service (OpenAI, etc.)
    return ResponseSchema(
        message="AI description generation is not yet implemented",
        data={"description": "Coming soon..."},
    )
