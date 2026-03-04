from typing import List

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.core.exceptions import BadRequestException, NotFoundException
from app.modules.payments.models import Payment
from app.modules.payments.schemas import (
    PaymentCreate,
    PaymentResponse,
    PaymentWebhook,
)
from app.modules.packages.models import Package
from app.modules.properties.models import Property
from app.modules.users.models import User
from app.schemas.base import ResponseSchema

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post(
    "/create",
    response_model=ResponseSchema[PaymentResponse],
    status_code=201,
    summary="Create a payment order",
)
async def create_payment(
    data: PaymentCreate,
    current_user: User = Depends(get_current_user),
):
    """Create a payment for a property + package combination."""
    # Validate property exists and belongs to user
    prop = await Property.get(data.property_id)
    if not prop or prop.host_id != current_user.id:
        raise NotFoundException(detail="Property not found")

    # Validate package exists
    pkg = await Package.get(data.package_id)
    if not pkg or not pkg.is_active:
        raise NotFoundException(detail="Package not found")

    amount = pkg.price_per_day * pkg.duration_days

    payment = Payment(
        user_id=current_user.id,
        property_id=data.property_id,
        package_id=data.package_id,
        amount=amount,
        payment_method=data.payment_method,
        status="pending",
    )
    await payment.insert()
    return ResponseSchema(
        message="Payment created. Proceed to payment gateway.",
        data=PaymentResponse.model_validate(payment),
    )


@router.post(
    "/webhook",
    response_model=ResponseSchema,
    summary="Payment gateway webhook",
)
async def payment_webhook(data: PaymentWebhook):
    """Handle payment result from gateway. Activates package on success."""
    payment = await Payment.find_one(
        Payment.transaction_id == data.transaction_id
    )
    if not payment:
        raise NotFoundException(detail="Payment not found")

    payment.status = data.status
    if data.metadata:
        payment.metadata = data.metadata
    await payment.save_with_timestamp()

    # If payment completed, activate package on property
    if data.status == "completed":
        prop = await Property.get(payment.property_id)
        pkg = await Package.get(payment.package_id)
        if prop and pkg:
            from datetime import datetime, timedelta
            from app.modules.properties.models import ActivePackage

            prop.active_package = ActivePackage(
                package_id=pkg.id,
                tier=pkg.tier,
                package_score=pkg.package_score,
                boosts_remaining=pkg.free_boosts,
                started_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=pkg.duration_days),
            )
            prop.status = "active"
            await prop.save_with_timestamp()

    return ResponseSchema(message=f"Payment {data.status}")


@router.get(
    "/my",
    response_model=ResponseSchema[List[PaymentResponse]],
    summary="My payment history",
)
async def my_payments(
    current_user: User = Depends(get_current_user),
):
    """Get current user's payment history."""
    items = (
        await Payment.find(Payment.user_id == current_user.id)
        .sort(-Payment.created_at)
        .to_list()
    )
    return ResponseSchema(
        data=[PaymentResponse.model_validate(p) for p in items],
    )
