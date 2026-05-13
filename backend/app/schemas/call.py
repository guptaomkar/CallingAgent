# ============================================================
# Call Pydantic Schemas
# File: app/schemas/call.py
# ============================================================

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CallInitiateRequest(BaseModel):
    """Request to initiate a single call."""
    contact_id: int
    campaign_id: int


class CallStatusResponse(BaseModel):
    """Response with current call status."""
    session_id: str
    contact_id: int
    campaign_id: int
    call_status: str
    call_outcome: Optional[str] = None
    sentiment: Optional[str] = None
    duration_seconds: Optional[int] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    provider_call_id: Optional[str] = None

    model_config = {"from_attributes": True}


class BatchCallRequest(BaseModel):
    """Request to launch a batch calling campaign."""
    campaign_id: int
    max_concurrent: int = Field(default=10, ge=1, le=100)
    priority_contacts: Optional[list[int]] = None  # Contact IDs to call first


class BatchCallResponse(BaseModel):
    """Response after launching a batch call campaign."""
    campaign_id: int
    total_contacts_queued: int
    estimated_duration_minutes: int
    batch_job_id: str
    status: str = "queued"


class CallWebhookEvent(BaseModel):
    """Incoming webhook event from Vapi.ai or Twilio."""
    event_type: str
    call_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: Optional[str] = None
    data: Optional[dict] = None
