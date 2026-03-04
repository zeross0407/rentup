from typing import List

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.core.exceptions import ForbiddenException, NotFoundException
from app.modules.reports.models import Report
from app.modules.reports.schemas import (
    ReportAdminUpdate,
    ReportCreate,
    ReportResponse,
)
from app.modules.users.models import User
from app.schemas.base import ResponseSchema

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post(
    "",
    response_model=ResponseSchema[ReportResponse],
    status_code=201,
    summary="Report a property",
)
async def create_report(
    data: ReportCreate,
    current_user: User = Depends(get_current_user),
):
    """Report a property listing for violations."""
    report = Report(
        reporter_id=current_user.id,
        property_id=data.property_id,
        reason=data.reason,
        description=data.description,
        attachments=data.attachments,
    )
    await report.insert()
    return ResponseSchema(
        message="Report submitted",
        data=ReportResponse.model_validate(report),
    )


@router.get(
    "",
    response_model=ResponseSchema[List[ReportResponse]],
    summary="List reports (Admin)",
)
async def list_reports(
    current_user: User = Depends(get_current_user),
):
    """List all reports. Admin only."""
    if current_user.role != "admin":
        raise ForbiddenException(detail="Admin only")

    items = (
        await Report.find()
        .sort(-Report.created_at)
        .to_list()
    )
    return ResponseSchema(
        data=[ReportResponse.model_validate(r) for r in items],
    )


@router.patch(
    "/{report_id}",
    response_model=ResponseSchema[ReportResponse],
    summary="Update report (Admin)",
)
async def update_report(
    report_id: str,
    data: ReportAdminUpdate,
    current_user: User = Depends(get_current_user),
):
    """Admin reviews and resolves a report."""
    if current_user.role != "admin":
        raise ForbiddenException(detail="Admin only")

    report = await Report.get(PydanticObjectId(report_id))
    if not report:
        raise NotFoundException(detail="Report not found")

    report.status = data.status
    if data.admin_note:
        report.admin_note = data.admin_note
    await report.save_with_timestamp()
    return ResponseSchema(
        message=f"Report {data.status}",
        data=ReportResponse.model_validate(report),
    )
