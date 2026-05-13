# ============================================================
# Campaign API Routes
# File: app/api/campaigns.py
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.campaign import Campaign, CampaignStatus
from app.schemas.campaign import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignListResponse,
)

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


@router.post("/", response_model=CampaignResponse, status_code=201)
async def create_campaign(
    payload: CampaignCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new calling campaign."""
    # Check for duplicate campaign_id
    existing = await db.execute(
        select(Campaign).where(Campaign.campaign_id == payload.campaign_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Campaign ID already exists")

    campaign = Campaign(
        campaign_id=payload.campaign_id,
        name=payload.name,
        agent_name=payload.agent_name,
        company_name=payload.company_name,
        service_name=payload.service_name,
        service_description=payload.service_description,
        campaign_objective=payload.campaign_objective,
        language=payload.language,
        max_call_duration_seconds=payload.max_call_duration_seconds,
        retry_attempts=payload.retry_attempts,
        retry_interval_hours=payload.retry_interval_hours,
        questions=[q.model_dump() for q in payload.questions],
        voice_id=payload.voice_id,
        tone=payload.tone,
    )
    db.add(campaign)
    await db.flush()
    await db.refresh(campaign)
    return campaign


@router.get("/", response_model=CampaignListResponse)
async def list_campaigns(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List all campaigns with pagination."""
    query = select(Campaign)
    if status:
        query = query.where(Campaign.status == status)
    query = query.order_by(Campaign.created_at.desc())

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # Paginate
    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    campaigns = result.scalars().all()

    return CampaignListResponse(
        campaigns=campaigns,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single campaign by ID."""
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: int,
    payload: CampaignUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a campaign."""
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "questions" in update_data and update_data["questions"] is not None:
        update_data["questions"] = [q if isinstance(q, dict) else q.model_dump() for q in update_data["questions"]]
    if "status" in update_data:
        update_data["status"] = CampaignStatus(update_data["status"])

    for key, value in update_data.items():
        setattr(campaign, key, value)

    await db.flush()
    await db.refresh(campaign)
    return campaign


@router.delete("/{campaign_id}", status_code=204)
async def delete_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a campaign and all related data."""
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    await db.delete(campaign)
