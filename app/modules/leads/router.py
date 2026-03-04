from typing import List

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundException
from app.modules.leads.models import Lead
from app.modules.leads.schemas import LeadCreate, LeadResponse, LeadStatsResponse
from app.modules.properties.models import Property
from app.modules.users.models import User
from app.schemas.base import ResponseSchema

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.post(
    "",
    response_model=ResponseSchema,
    status_code=201,
    summary="Record a lead action",
)
async def create_lead(
    data: LeadCreate,
    current_user: User = Depends(get_current_user),
):
    """Record a tenant action (view, click phone, save, share) on a property."""
    prop = await Property.get(data.property_id)
    if not prop:
        raise NotFoundException(detail="Property not found")

    lead = Lead(
        tenant_id=current_user.id,
        property_id=data.property_id,
        host_id=prop.host_id,
        action=data.action,
    )
    await lead.insert()

    # Update property metrics
    action_map = {
        "view_detail": "views",
        "click_phone": "phone_clicks",
        "save": "saves",
        "share": "shares",
    }
    metric_field = action_map.get(data.action)
    if metric_field:
        current_val = getattr(prop.metrics, metric_field, 0)
        setattr(prop.metrics, metric_field, current_val + 1)
        await prop.save_with_timestamp()

    return ResponseSchema(message="Lead recorded")


@router.get(
    "/my",
    response_model=ResponseSchema[List[LeadResponse]],
    summary="My leads (Host dashboard)",
)
async def my_leads(
    current_user: User = Depends(get_current_user),
):
    """Get leads (tenant actions) on the host's properties."""
    items = (
        await Lead.find(Lead.host_id == current_user.id)
        .sort(-Lead.created_at)
        .limit(100)
        .to_list()
    )
    return ResponseSchema(
        data=[LeadResponse.model_validate(l) for l in items],
    )


@router.get(
    "/stats",
    response_model=ResponseSchema[LeadStatsResponse],
    summary="Lead statistics (Host)",
)
async def lead_stats(
    current_user: User = Depends(get_current_user),
):
    """Get aggregated lead statistics for the host's properties."""
    collection = Lead.get_motor_collection()
    pipeline = [
        {"$match": {"host_id": current_user.id}},
        {"$group": {
            "_id": "$action",
            "count": {"$sum": 1},
            "tenants": {"$addToSet": "$tenant_id"},
        }},
    ]
    results = await collection.aggregate(pipeline).to_list(length=10)

    stats = LeadStatsResponse()
    all_tenants = set()
    for r in results:
        action = r["_id"]
        count = r["count"]
        all_tenants.update(r.get("tenants", []))
        if action == "view_detail":
            stats.total_views = count
        elif action == "click_phone":
            stats.total_phone_clicks = count
        elif action == "save":
            stats.total_saves = count
        elif action == "share":
            stats.total_shares = count
    stats.unique_tenants = len(all_tenants)

    return ResponseSchema(data=stats)
