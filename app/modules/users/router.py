from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.users.schemas import (
    UpgradeHostRequest,
    UserResponse,
    UserUpdate,
)
from app.schemas.base import ResponseSchema

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=ResponseSchema[UserResponse],
    summary="Get current user profile",
)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get the profile of the currently authenticated user."""
    return ResponseSchema(data=UserResponse.model_validate(current_user))


@router.put(
    "/me",
    response_model=ResponseSchema[UserResponse],
    summary="Update current user profile",
)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
):
    """Update the current user's profile info."""
    update_data = data.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)
    await current_user.save_with_timestamp()
    return ResponseSchema(
        message="Profile updated",
        data=UserResponse.model_validate(current_user),
    )


@router.post(
    "/me/upgrade-host",
    response_model=ResponseSchema[UserResponse],
    summary="Submit identity to upgrade to Host",
)
async def upgrade_to_host(
    data: UpgradeHostRequest,
    current_user: User = Depends(get_current_user),
):
    """Submit CCCD/CMND info to upgrade from Tenant to Host role."""
    from app.modules.users.models import UserIdentity

    current_user.identity = UserIdentity(
        id_number=data.id_number,
        issued_date=data.issued_date,
        issued_place=data.issued_place,
        front_image_url=data.front_image_url,
        back_image_url=data.back_image_url,
        verified=False,
    )
    current_user.role = "host"
    await current_user.save_with_timestamp()
    return ResponseSchema(
        message="Upgraded to Host. Identity pending verification.",
        data=UserResponse.model_validate(current_user),
    )


@router.get(
    "/{user_id}",
    response_model=ResponseSchema[UserResponse],
    summary="Get user by ID (Admin)",
)
async def get_user(user_id: str):
    """Get a user's profile by ID. Admin only."""
    from beanie import PydanticObjectId

    user = await User.get(PydanticObjectId(user_id))
    if not user:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(detail="User not found")
    return ResponseSchema(data=UserResponse.model_validate(user))
