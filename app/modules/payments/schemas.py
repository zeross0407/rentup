from datetime import datetime
from typing import Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, Field


# ──── Request Schemas ────


class PaymentCreate(BaseModel):
    """Create a payment for a property + package."""
    property_id: PydanticObjectId
    package_id: PydanticObjectId
    payment_method: str = Field(
        ..., pattern="^(momo|vnpay|bank_transfer)$"
    )


class PaymentWebhook(BaseModel):
    """Webhook payload from payment gateway."""
    transaction_id: str
    status: str = Field(..., pattern="^(completed|failed)$")
    metadata: Optional[dict] = None


# ──── Response Schemas ────


class PaymentResponse(BaseModel):
    """Payment transaction response."""
    id: PydanticObjectId = Field(..., alias="_id")
    user_id: PydanticObjectId
    property_id: PydanticObjectId
    package_id: PydanticObjectId
    amount: int
    payment_method: str
    status: str
    transaction_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}
