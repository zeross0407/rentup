from datetime import datetime
from typing import Dict, List, Optional

from beanie import Indexed, PydanticObjectId
from pydantic import BaseModel, Field

from app.models.base import BaseDocument, TimestampDocument


# ──── Embedded Sub-Models ────


class LastMessage(BaseModel):
    """Embedded last message snapshot for conversation preview."""
    content: str
    sender_id: PydanticObjectId
    sent_at: datetime


# ──── Conversation Document ────


class Conversation(BaseDocument):
    """Chat conversation between two users."""

    participants: List[PydanticObjectId]  # [tenant_id, host_id]
    property_id: Optional[PydanticObjectId] = None
    last_message: Optional[LastMessage] = None
    unread_count: Dict[str, int] = Field(default_factory=dict)

    class Settings:
        name = "conversations"
        indexes = [
            "participants",
            [("participants", 1), ("updated_at", -1)],
        ]


# ──── Message Document ────


class FileMetadata(BaseModel):
    """Embedded file metadata for non-text messages."""
    filename: str
    size: int
    mime_type: str


class Message(TimestampDocument):
    """Chat message within a conversation."""

    conversation_id: Indexed(PydanticObjectId)
    sender_id: PydanticObjectId
    content_type: str = Field(
        default="text", pattern="^(text|image|file)$"
    )
    content: str
    file_metadata: Optional[FileMetadata] = None
    is_read: bool = Field(default=False)

    class Settings:
        name = "messages"
        indexes = [
            [("conversation_id", 1), ("created_at", -1)],
            "sender_id",
        ]
