# ============================================================
# Report API Routes
# File: app/api/reports.py
# ============================================================

import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.campaign import Campaign
from app.schemas.report import ReportRequest, ReportResponse

router = APIRouter(prefix="/reports", tags=["Reports"])

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    payload: ReportRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate an Excel report for a campaign."""
    campaign = await db.get(Campaign, payload.campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    from app.services.report_writer import ReportWriter

    writer = ReportWriter(db)
    report_id = str(uuid.uuid4())[:8]
    filename = f"report_{campaign.campaign_id}_{report_id}.xlsx"
    filepath = os.path.join(REPORTS_DIR, filename)

    stats = await writer.generate_report(
        campaign_id=payload.campaign_id,
        filepath=filepath,
        include_tabs=payload.include_tabs,
        date_from=payload.date_from,
        date_to=payload.date_to,
    )

    return ReportResponse(
        report_id=report_id,
        campaign_id=payload.campaign_id,
        filename=filename,
        download_url=f"/api/v1/reports/download/{filename}",
        generated_at=datetime.utcnow(),
        stats=stats,
    )


@router.get("/download/{filename}")
async def download_report(filename: str):
    """Download a generated Excel report."""
    filepath = os.path.join(REPORTS_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report file not found")

    return FileResponse(
        filepath,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename,
    )
