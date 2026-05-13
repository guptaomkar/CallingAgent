# ============================================================
# Contact API Routes
# File: app/api/contacts.py
# ============================================================

import io
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.contact import Contact
from app.models.campaign import Campaign
from app.schemas.contact import (
    ContactCreate,
    ContactResponse,
    ContactListResponse,
    ContactUploadResponse,
)

router = APIRouter(prefix="/contacts", tags=["Contacts"])


@router.post("/{campaign_id}/upload", response_model=ContactUploadResponse)
async def upload_contacts(
    campaign_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload an Excel/CSV file of contacts for a campaign."""
    # Verify campaign exists
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Validate file type
    if not file.filename.endswith((".xlsx", ".csv")):
        raise HTTPException(
            status_code=400,
            detail="Only .xlsx and .csv files are supported",
        )

    # Delegate to input processor service
    from app.services.input_processor import InputProcessor

    processor = InputProcessor(db)
    content = await file.read()
    result = await processor.process_file(
        file_content=content,
        filename=file.filename,
        campaign_id=campaign_id,
    )
    return result


@router.get("/{campaign_id}", response_model=ContactListResponse)
async def list_contacts(
    campaign_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List contacts for a campaign with pagination."""
    query = select(Contact).where(Contact.campaign_id == campaign_id)
    if status:
        query = query.where(Contact.status == status)
    query = query.order_by(Contact.created_at.desc())

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # Paginate
    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    contacts = result.scalars().all()

    return ContactListResponse(
        contacts=contacts,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/{campaign_id}/manual", response_model=ContactResponse, status_code=201)
async def add_contact(
    campaign_id: int,
    payload: ContactCreate,
    db: AsyncSession = Depends(get_db),
):
    """Manually add a single contact to a campaign."""
    # Verify campaign
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Campaign not found")

    contact = Contact(
        campaign_id=campaign_id,
        client_name=payload.client_name,
        phone_number=payload.phone_number,
        email=payload.email,
        preferred_language=payload.preferred_language,
        notes=payload.notes,
    )
    db.add(contact)
    await db.flush()
    await db.refresh(contact)
    return contact


@router.delete("/contact/{contact_id}", status_code=204)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a single contact."""
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    await db.delete(contact)
