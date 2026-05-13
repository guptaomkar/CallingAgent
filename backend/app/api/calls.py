# ============================================================
# Call Management API Routes
# File: app/api/calls.py
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.call_session import CallSession, CallStatus
from app.models.contact import Contact
from app.models.campaign import Campaign
from app.schemas.call import (
    CallInitiateRequest,
    CallStatusResponse,
    BatchCallRequest,
    BatchCallResponse,
)

router = APIRouter(prefix="/calls", tags=["Calls"])


@router.post("/initiate", response_model=CallStatusResponse)
async def initiate_call(
    payload: CallInitiateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Initiate a single outbound call to a contact."""
    # Verify contact and campaign exist
    contact = await db.get(Contact, payload.contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    campaign = await db.get(Campaign, payload.campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Check DND / blacklist
    if contact.is_dnd or contact.is_blacklisted:
        raise HTTPException(
            status_code=403,
            detail="Contact is on DND or blacklisted",
        )

    # Create call session
    session = CallSession(
        contact_id=payload.contact_id,
        campaign_id=payload.campaign_id,
        call_status=CallStatus.INITIATED,
    )
    db.add(session)
    await db.flush()
    await db.refresh(session)

    # Queue the call execution via Celery
    from app.tasks.call_tasks import execute_single_call

    execute_single_call.delay(session.id)

    return CallStatusResponse(
        session_id=str(session.session_id),
        contact_id=session.contact_id,
        campaign_id=session.campaign_id,
        call_status=session.call_status.value,
        started_at=session.started_at,
    )


@router.post("/batch", response_model=BatchCallResponse)
async def launch_batch_calls(
    payload: BatchCallRequest,
    db: AsyncSession = Depends(get_db),
):
    """Launch a batch calling campaign for all pending contacts."""
    campaign = await db.get(Campaign, payload.campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Count pending contacts
    count_query = select(func.count()).select_from(
        select(Contact)
        .where(Contact.campaign_id == payload.campaign_id)
        .where(Contact.status == "pending")
        .where(Contact.is_dnd == False)
        .where(Contact.is_blacklisted == False)
        .subquery()
    )
    total_pending = (await db.execute(count_query)).scalar()

    if total_pending == 0:
        raise HTTPException(status_code=400, detail="No pending contacts to call")

    # Launch batch via Celery
    from app.tasks.batch_tasks import launch_campaign

    job = launch_campaign.delay(
        campaign_id=payload.campaign_id,
        max_concurrent=payload.max_concurrent,
    )

    # Estimate duration: ~5 min per call / concurrent slots
    estimated_minutes = int((total_pending * 5) / payload.max_concurrent)

    return BatchCallResponse(
        campaign_id=payload.campaign_id,
        total_contacts_queued=total_pending,
        estimated_duration_minutes=estimated_minutes,
        batch_job_id=str(job.id),
        status="queued",
    )


@router.get("/status/{session_id}", response_model=CallStatusResponse)
async def get_call_status(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get the current status of a call by session ID."""
    result = await db.execute(
        select(CallSession).where(CallSession.session_id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Call session not found")

    return CallStatusResponse(
        session_id=str(session.session_id),
        contact_id=session.contact_id,
        campaign_id=session.campaign_id,
        call_status=session.call_status.value,
        call_outcome=session.call_outcome.value if session.call_outcome else None,
        sentiment=session.sentiment.value if session.sentiment else None,
        duration_seconds=session.duration_seconds,
        started_at=session.started_at,
        ended_at=session.ended_at,
        provider_call_id=session.provider_call_id,
    )


@router.get("/campaign/{campaign_id}")
async def list_campaign_calls(
    campaign_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List all call sessions for a campaign."""
    query = select(CallSession).where(CallSession.campaign_id == campaign_id)
    if status:
        query = query.where(CallSession.call_status == status)
    query = query.order_by(CallSession.created_at.desc())

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    sessions = result.scalars().all()

    return {
        "calls": [
            CallStatusResponse(
                session_id=str(s.session_id),
                contact_id=s.contact_id,
                campaign_id=s.campaign_id,
                call_status=s.call_status.value,
                call_outcome=s.call_outcome.value if s.call_outcome else None,
                sentiment=s.sentiment.value if s.sentiment else None,
                duration_seconds=s.duration_seconds,
                started_at=s.started_at,
                ended_at=s.ended_at,
                provider_call_id=s.provider_call_id,
            )
            for s in sessions
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
