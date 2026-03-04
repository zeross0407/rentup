from typing import List

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.core.exceptions import ForbiddenException, NotFoundException
from app.modules.appointments.models import Appointment
from app.modules.appointments.schemas import (
    AppointmentCreate,
    AppointmentReschedule,
    AppointmentResponse,
)
from app.modules.properties.models import Property
from app.modules.users.models import User
from app.schemas.base import ResponseSchema

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post(
    "",
    response_model=ResponseSchema[AppointmentResponse],
    status_code=201,
    summary="Request a viewing appointment",
)
async def create_appointment(
    data: AppointmentCreate,
    current_user: User = Depends(get_current_user),
):
    """Tenant creates a viewing appointment for a property."""
    prop = await Property.get(data.property_id)
    if not prop:
        raise NotFoundException(detail="Property not found")

    appt = Appointment(
        tenant_id=current_user.id,
        host_id=prop.host_id,
        property_id=data.property_id,
        proposed_time=data.proposed_time,
        note=data.note,
    )
    await appt.insert()
    return ResponseSchema(
        message="Appointment requested",
        data=AppointmentResponse.model_validate(appt),
    )


@router.get(
    "",
    response_model=ResponseSchema[List[AppointmentResponse]],
    summary="List my appointments",
)
async def list_appointments(
    current_user: User = Depends(get_current_user),
):
    """List appointments for the current user (as tenant or host)."""
    items = await Appointment.find(
        {"$or": [
            {"tenant_id": current_user.id},
            {"host_id": current_user.id},
        ]}
    ).sort(-Appointment.created_at).to_list()

    return ResponseSchema(
        data=[AppointmentResponse.model_validate(a) for a in items],
    )


@router.patch(
    "/{appointment_id}/confirm",
    response_model=ResponseSchema[AppointmentResponse],
    summary="Confirm appointment (Host)",
)
async def confirm_appointment(
    appointment_id: str,
    current_user: User = Depends(get_current_user),
):
    """Host confirms a pending appointment."""
    appt = await Appointment.get(PydanticObjectId(appointment_id))
    if not appt:
        raise NotFoundException(detail="Appointment not found")
    if appt.host_id != current_user.id:
        raise ForbiddenException()

    appt.status = "confirmed"
    await appt.save_with_timestamp()
    return ResponseSchema(
        message="Appointment confirmed",
        data=AppointmentResponse.model_validate(appt),
    )


@router.patch(
    "/{appointment_id}/reject",
    response_model=ResponseSchema[AppointmentResponse],
    summary="Reject appointment (Host)",
)
async def reject_appointment(
    appointment_id: str,
    current_user: User = Depends(get_current_user),
):
    """Host rejects a pending appointment."""
    appt = await Appointment.get(PydanticObjectId(appointment_id))
    if not appt:
        raise NotFoundException(detail="Appointment not found")
    if appt.host_id != current_user.id:
        raise ForbiddenException()

    appt.status = "rejected"
    await appt.save_with_timestamp()
    return ResponseSchema(
        message="Appointment rejected",
        data=AppointmentResponse.model_validate(appt),
    )


@router.patch(
    "/{appointment_id}/reschedule",
    response_model=ResponseSchema[AppointmentResponse],
    summary="Reschedule appointment (Host)",
)
async def reschedule_appointment(
    appointment_id: str,
    data: AppointmentReschedule,
    current_user: User = Depends(get_current_user),
):
    """Host proposes an alternative time."""
    appt = await Appointment.get(PydanticObjectId(appointment_id))
    if not appt:
        raise NotFoundException(detail="Appointment not found")
    if appt.host_id != current_user.id:
        raise ForbiddenException()

    appt.alternative_time = data.alternative_time
    appt.status = "rescheduled"
    await appt.save_with_timestamp()
    return ResponseSchema(
        message="Alternative time proposed",
        data=AppointmentResponse.model_validate(appt),
    )


@router.patch(
    "/{appointment_id}/cancel",
    response_model=ResponseSchema[AppointmentResponse],
    summary="Cancel appointment (Tenant)",
)
async def cancel_appointment(
    appointment_id: str,
    current_user: User = Depends(get_current_user),
):
    """Tenant cancels their appointment."""
    appt = await Appointment.get(PydanticObjectId(appointment_id))
    if not appt:
        raise NotFoundException(detail="Appointment not found")
    if appt.tenant_id != current_user.id:
        raise ForbiddenException()

    appt.status = "cancelled"
    await appt.save_with_timestamp()
    return ResponseSchema(
        message="Appointment cancelled",
        data=AppointmentResponse.model_validate(appt),
    )
