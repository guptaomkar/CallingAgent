# ============================================================
# Contact Pydantic Schemas
# File: app/schemas/contact.py
# ============================================================

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ContactCreate(BaseModel):
    """Schema for creating a single contact."""
    client_name: str = Field(..., max_length=200)
    phone_number: str = Field(..., max_length=20, description="E.164 format: +91XXXXXXXXXX")
    email: Optional[str] = Field(None, max_length=200)
    preferred_language: Optional[str] = None
    notes: Optional[str] = None


class ContactResponse(BaseModel):
    """Schema for contact API response."""
    id: int
    campaign_id: int
    client_name: str
    phone_number: str
    email: Optional[str]
    preferred_language: Optional[str]
    status: str
    is_dnd: bool
    is_blacklisted: bool
    last_contacted: Optional[datetime]
    retry_count: int
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ContactListResponse(BaseModel):
    """Paginated contact list response."""
    contacts: list[ContactResponse]
    total: int
    page: int
    page_size: int


class ContactUploadResponse(BaseModel):
    """Response after uploading a contact file."""
    total_rows: int
    valid_contacts: int
    duplicates_skipped: int
    invalid_rows: int
    dnd_excluded: int
    errors: list[dict] = Field(default_factory=list)
