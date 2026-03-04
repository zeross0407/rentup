from typing import List

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.modules.properties.schemas import PropertyListResponse
from app.modules.properties.models import Property
from app.modules.view_history.models import ViewHistory
from app.modules.users.models import User
from app.schemas.base import ResponseSchema

router = APIRouter(prefix="/view-history", tags=["View History"])


@router.post(
    "/{property_id}",
    response_model=ResponseSchema,
    summary="Record property view",
)
async def record_view(
    property_id: str,
    current_user: User = Depends(get_current_user),
):
    """Record that the user viewed a property."""
    pid = PydanticObjectId(property_id)
    view = ViewHistory(user_id=current_user.id, property_id=pid)
    await view.insert()

    # Increment view count on property
    prop = await Property.get(pid)
    if prop:
        prop.metrics.views += 1
        await prop.save_with_timestamp()

    return ResponseSchema(message="View recorded")


@router.get(
    "",
    response_model=ResponseSchema[List[PropertyListResponse]],
    summary="Get view history",
)
async def get_view_history(
    current_user: User = Depends(get_current_user),
):
    """Get the current user's recently viewed properties."""
    views = (
        await ViewHistory.find(ViewHistory.user_id == current_user.id)
        .sort(-ViewHistory.viewed_at)
        .limit(50)
        .to_list()
    )
    property_ids = list(dict.fromkeys(v.property_id for v in views))
    if not property_ids:
        return ResponseSchema(data=[])

    properties = await Property.find({"_id": {"$in": property_ids}}).to_list()
    prop_map = {p.id: p for p in properties}
    ordered = [
        PropertyListResponse.model_validate(prop_map[pid])
        for pid in property_ids if pid in prop_map
    ]
    return ResponseSchema(data=ordered)
