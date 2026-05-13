# ============================================================
# Campaign Pydantic Schemas
# File: app/schemas/campaign.py
# ============================================================

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class QuestionItem(BaseModel):
    """A single question in the campaign question list."""
    id: str = Field(..., description="Unique question ID, e.g. 'q1'")
    text: str = Field(..., description="The question text to ask the client")


class CampaignCreate(BaseModel):
    """Schema for creating a new campaign."""
    campaign_id: str = Field(..., max_length=50, description="Unique campaign identifier")
    name: str = Field(..., max_length=200, description="Campaign name")

    agent_name: str = Field(..., max_length=100)
    company_name: str = Field(..., max_length=200)

    service_name: str = Field(..., max_length=200)
    service_description: str
    campaign_objective: str

    language: str = Field(default="English", max_length=50)
    max_call_duration_seconds: int = Field(default=300, ge=60, le=1800)
    retry_attempts: int = Field(default=3, ge=0, le=10)
    retry_interval_hours: int = Field(default=24, ge=1, le=168)

    questions: list[QuestionItem] = Field(
        ...,
        min_length=1,
        max_length=20,
        description="List of questions to ask during the call",
    )

    voice_id: Optional[str] = None
    tone: str = Field(default="professional_warm", max_length=50)


class CampaignUpdate(BaseModel):
    """Schema for updating an existing campaign."""
    name: Optional[str] = None
    agent_name: Optional[str] = None
    company_name: Optional[str] = None
    service_name: Optional[str] = None
    service_description: Optional[str] = None
    campaign_objective: Optional[str] = None
    language: Optional[str] = None
    max_call_duration_seconds: Optional[int] = None
    retry_attempts: Optional[int] = None
    retry_interval_hours: Optional[int] = None
    questions: Optional[list[QuestionItem]] = None
    voice_id: Optional[str] = None
    tone: Optional[str] = None
    status: Optional[str] = None


class CampaignResponse(BaseModel):
    """Schema for campaign API response."""
    id: int
    campaign_id: str
    name: str
    agent_name: str
    company_name: str
    service_name: str
    service_description: str
    campaign_objective: str
    language: str
    max_call_duration_seconds: int
    retry_attempts: int
    retry_interval_hours: int
    questions: list[dict]
    voice_id: Optional[str]
    tone: str
    status: str
    total_contacts: int
    calls_completed: int
    calls_interested: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CampaignListResponse(BaseModel):
    """Paginated campaign list response."""
    campaigns: list[CampaignResponse]
    total: int
    page: int
    page_size: int
