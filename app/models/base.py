from datetime import datetime
from typing import Optional

from beanie import Document
from pydantic import Field


class BaseDocument(Document):
    """Base document with common fields for all MongoDB collections."""

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    async def save_with_timestamp(self, **kwargs):
        """Save document and update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
        await self.save(**kwargs)

    class Settings:
        # Use this as base; subclasses override collection name
        use_state_management = True
