from datetime import datetime
from typing import Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, Field


class NotificationResponse(BaseModel):
    """Notification response."""
    id: PydanticObjectId = Field(..., alias="_id")
    user_id: PydanticObjectId
    type: str
    title: str
    body: str
    data: Optional[dict] = None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}
