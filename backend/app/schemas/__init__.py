# app/schemas/__init__.py
from app.schemas.campaign import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignListResponse,
)
from app.schemas.contact import (
    ContactCreate,
    ContactResponse,
    ContactListResponse,
    ContactUploadResponse,
)
from app.schemas.call import (
    CallInitiateRequest,
    CallStatusResponse,
    BatchCallRequest,
    BatchCallResponse,
)
from app.schemas.report import ReportRequest, ReportResponse

__all__ = [
    "CampaignCreate", "CampaignUpdate", "CampaignResponse", "CampaignListResponse",
    "ContactCreate", "ContactResponse", "ContactListResponse", "ContactUploadResponse",
    "CallInitiateRequest", "CallStatusResponse", "BatchCallRequest", "BatchCallResponse",
    "ReportRequest", "ReportResponse",
]
