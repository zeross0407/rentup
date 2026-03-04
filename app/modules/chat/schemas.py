from datetime import datetime
from typing import Dict, List, Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, Field


# ──── Request Schemas ────


class ConversationCreate(BaseModel):
    """Start or open a conversation."""
    participant_id: PydanticObjectId  # The other user
    property_id: Optional[PydanticObjectId] = None


class MessageCreate(BaseModel):
    """Send a message in a conversation."""
    content_type: str = Field(
        default="text", pattern="^(text|image|file)$"
    )
    content: str = Field(..., min_length=1, max_length=5000)
    file_metadata: Optional[dict] = None


# ──── Response Schemas ────


class LastMessageResponse(BaseModel):
    content: str
    sender_id: PydanticObjectId
    sent_at: datetime


class ConversationResponse(BaseModel):
    """Conversation list item."""
    id: PydanticObjectId = Field(..., alias="_id")
    participants: List[PydanticObjectId]
    property_id: Optional[PydanticObjectId] = None
    last_message: Optional[LastMessageResponse] = None
    unread_count: Dict[str, int] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class MessageResponse(BaseModel):
    """Message in a conversation."""
    id: PydanticObjectId = Field(..., alias="_id")
    conversation_id: PydanticObjectId
    sender_id: PydanticObjectId
    content_type: str
    content: str
    file_metadata: Optional[dict] = None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}
