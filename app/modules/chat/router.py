from datetime import datetime
from typing import List

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_current_user
from app.core.exceptions import ForbiddenException, NotFoundException
from app.modules.chat.models import Conversation, LastMessage, Message
from app.modules.chat.schemas import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
)
from app.modules.users.models import User
from app.schemas.base import ResponseSchema

router = APIRouter(prefix="/conversations", tags=["Chat"])


@router.post(
    "",
    response_model=ResponseSchema[ConversationResponse],
    summary="Start or open a conversation",
)
async def create_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user),
):
    """Start a new conversation or return existing one between two users."""
    participants = sorted([current_user.id, data.participant_id])

    # Check if conversation already exists
    existing = await Conversation.find_one(
        Conversation.participants == participants,
    )
    if existing:
        return ResponseSchema(data=ConversationResponse.model_validate(existing))

    conv = Conversation(
        participants=participants,
        property_id=data.property_id,
    )
    await conv.insert()
    return ResponseSchema(
        message="Conversation created",
        data=ConversationResponse.model_validate(conv),
    )


@router.get(
    "",
    response_model=ResponseSchema[List[ConversationResponse]],
    summary="List my conversations",
)
async def list_conversations(
    current_user: User = Depends(get_current_user),
):
    """List all conversations for the current user."""
    items = (
        await Conversation.find({"participants": current_user.id})
        .sort(-Conversation.updated_at)
        .to_list()
    )
    return ResponseSchema(
        data=[ConversationResponse.model_validate(c) for c in items],
    )


@router.get(
    "/{conversation_id}/messages",
    response_model=ResponseSchema[List[MessageResponse]],
    summary="Get messages in a conversation",
)
async def get_messages(
    conversation_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=100),
    current_user: User = Depends(get_current_user),
):
    """Get paginated messages in a conversation."""
    conv_id = PydanticObjectId(conversation_id)
    conv = await Conversation.get(conv_id)
    if not conv or current_user.id not in conv.participants:
        raise ForbiddenException()

    skip = (page - 1) * page_size
    items = (
        await Message.find(Message.conversation_id == conv_id)
        .sort(-Message.created_at)
        .skip(skip)
        .limit(page_size)
        .to_list()
    )
    return ResponseSchema(
        data=[MessageResponse.model_validate(m) for m in items],
    )


@router.post(
    "/{conversation_id}/messages",
    response_model=ResponseSchema[MessageResponse],
    status_code=201,
    summary="Send a message",
)
async def send_message(
    conversation_id: str,
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
):
    """Send a message in a conversation."""
    conv_id = PydanticObjectId(conversation_id)
    conv = await Conversation.get(conv_id)
    if not conv or current_user.id not in conv.participants:
        raise ForbiddenException()

    from app.modules.chat.models import FileMetadata

    msg = Message(
        conversation_id=conv_id,
        sender_id=current_user.id,
        content_type=data.content_type,
        content=data.content,
        file_metadata=(
            FileMetadata(**data.file_metadata)
            if data.file_metadata else None
        ),
    )
    await msg.insert()

    # Update conversation's last message and unread count
    conv.last_message = LastMessage(
        content=data.content,
        sender_id=current_user.id,
        sent_at=datetime.utcnow(),
    )
    # Increment unread for the other participant
    for pid in conv.participants:
        if pid != current_user.id:
            key = str(pid)
            conv.unread_count[key] = conv.unread_count.get(key, 0) + 1
    await conv.save_with_timestamp()

    return ResponseSchema(
        message="Message sent",
        data=MessageResponse.model_validate(msg),
    )


@router.patch(
    "/{conversation_id}/read",
    response_model=ResponseSchema,
    summary="Mark conversation as read",
)
async def mark_read(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
):
    """Mark all messages in a conversation as read for the current user."""
    conv_id = PydanticObjectId(conversation_id)
    conv = await Conversation.get(conv_id)
    if not conv or current_user.id not in conv.participants:
        raise ForbiddenException()

    conv.unread_count[str(current_user.id)] = 0
    await conv.save_with_timestamp()

    # Mark individual messages as read
    await Message.find(
        Message.conversation_id == conv_id,
        Message.sender_id != current_user.id,
        Message.is_read == False,
    ).update({"$set": {"is_read": True}})

    return ResponseSchema(message="Marked as read")
