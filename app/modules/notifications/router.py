from typing import List

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundException
from app.modules.notifications.models import Notification
from app.modules.notifications.schemas import NotificationResponse
from app.modules.users.models import User
from app.schemas.base import ResponseSchema

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get(
    "",
    response_model=ResponseSchema[List[NotificationResponse]],
    summary="List my notifications",
)
async def list_notifications(
    current_user: User = Depends(get_current_user),
):
    """Get the current user's notifications."""
    items = (
        await Notification.find(Notification.user_id == current_user.id)
        .sort(-Notification.created_at)
        .limit(50)
        .to_list()
    )
    return ResponseSchema(
        data=[NotificationResponse.model_validate(n) for n in items],
    )


@router.patch(
    "/{notification_id}/read",
    response_model=ResponseSchema,
    summary="Mark notification as read",
)
async def mark_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
):
    """Mark a single notification as read."""
    notif = await Notification.get(PydanticObjectId(notification_id))
    if not notif or notif.user_id != current_user.id:
        raise NotFoundException(detail="Notification not found")

    notif.is_read = True
    await notif.save()
    return ResponseSchema(message="Marked as read")


@router.patch(
    "/read-all",
    response_model=ResponseSchema,
    summary="Mark all notifications as read",
)
async def mark_all_read(
    current_user: User = Depends(get_current_user),
):
    """Mark all of the current user's notifications as read."""
    await Notification.find(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).update({"$set": {"is_read": True}})
    return ResponseSchema(message="All notifications marked as read")
