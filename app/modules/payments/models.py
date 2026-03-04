from typing import Optional

from beanie import Indexed, PydanticObjectId
from pydantic import Field

from app.models.base import BaseDocument


class Payment(BaseDocument):
    """Payment transaction document."""

    user_id: Indexed(PydanticObjectId)
    property_id: Indexed(PydanticObjectId)
    package_id: PydanticObjectId
    amount: int = Field(..., gt=0)
    payment_method: str = Field(
        ..., pattern="^(momo|vnpay|bank_transfer)$"
    )
    status: str = Field(
        default="pending",
        pattern="^(pending|completed|failed|refunded)$",
    )
    transaction_id: Optional[str] = None
    metadata: Optional[dict] = None

    class Settings:
        name = "payments"
        indexes = [
            [("user_id", 1), ("created_at", -1)],
            "property_id",
            "status",
            "transaction_id",
        ]
