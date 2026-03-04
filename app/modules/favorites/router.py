from typing import List

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.modules.favorites.models import Favorite
from app.modules.properties.models import Property
from app.modules.properties.schemas import PropertyListResponse
from app.modules.users.models import User
from app.schemas.base import ResponseSchema

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.post(
    "/{property_id}",
    response_model=ResponseSchema,
    summary="Toggle favorite",
)
async def toggle_favorite(
    property_id: str,
    current_user: User = Depends(get_current_user),
):
    """Toggle a property as favorite. Add if not saved, remove if already saved."""
    pid = PydanticObjectId(property_id)
    existing = await Favorite.find_one(
        Favorite.user_id == current_user.id,
        Favorite.property_id == pid,
    )
    if existing:
        await existing.delete()
        return ResponseSchema(message="Removed from favorites")
    else:
        fav = Favorite(user_id=current_user.id, property_id=pid)
        await fav.insert()
        return ResponseSchema(message="Added to favorites")


@router.get(
    "",
    response_model=ResponseSchema[List[PropertyListResponse]],
    summary="List saved properties",
)
async def list_favorites(
    current_user: User = Depends(get_current_user),
):
    """Get the current user's saved/favorite properties."""
    favs = (
        await Favorite.find(Favorite.user_id == current_user.id)
        .sort(-Favorite.created_at)
        .to_list()
    )
    property_ids = [f.property_id for f in favs]
    if not property_ids:
        return ResponseSchema(data=[])

    properties = await Property.find({"_id": {"$in": property_ids}}).to_list()
    return ResponseSchema(
        data=[PropertyListResponse.model_validate(p) for p in properties],
    )
