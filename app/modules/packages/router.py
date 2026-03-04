from typing import List

from beanie import PydanticObjectId
from fastapi import APIRouter

from app.core.exceptions import NotFoundException
from app.modules.packages.models import Package
from app.modules.packages.schemas import PackageResponse
from app.schemas.base import ResponseSchema

router = APIRouter(prefix="/packages", tags=["Packages"])


@router.get(
    "",
    response_model=ResponseSchema[List[PackageResponse]],
    summary="List available packages",
)
async def list_packages():
    """List all active subscription packages."""
    items = await Package.find(Package.is_active == True).to_list()
    return ResponseSchema(
        data=[PackageResponse.model_validate(p) for p in items],
    )


@router.get(
    "/{package_id}",
    response_model=ResponseSchema[PackageResponse],
    summary="Get package details",
)
async def get_package(package_id: str):
    """Get a single package by ID."""
    pkg = await Package.get(PydanticObjectId(package_id))
    if not pkg:
        raise NotFoundException(detail="Package not found")
    return ResponseSchema(data=PackageResponse.model_validate(pkg))
