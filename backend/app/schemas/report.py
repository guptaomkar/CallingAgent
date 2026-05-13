# ============================================================
# Report Pydantic Schemas
# File: app/schemas/report.py
# ============================================================

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    """Request to generate a campaign report."""
    campaign_id: int
    include_tabs: list[str] = Field(
        default=["all_calls", "interested", "callbacks", "no_contact", "summary"],
        description="Which tabs to include in the Excel report",
    )
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class ReportResponse(BaseModel):
    """Response after report generation."""
    report_id: str
    campaign_id: int
    filename: str
    download_url: str
    generated_at: datetime
    stats: dict = Field(
        default_factory=dict,
        description="Summary statistics included in the report",
    )


class CampaignStats(BaseModel):
    """Campaign-level statistics for the summary tab."""
    total_calls_attempted: int = 0
    total_calls_connected: int = 0
    connection_rate: float = 0.0
    outcome_breakdown: dict = Field(default_factory=dict)
    average_call_duration: float = 0.0
    sentiment_split: dict = Field(default_factory=dict)
    demo_requests: int = 0
    email_requests: int = 0
