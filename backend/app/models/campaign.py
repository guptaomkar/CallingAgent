# ============================================================
# Campaign ORM Model
# File: app/models/campaign.py
# ============================================================

import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Campaign(Base):
    """Represents a calling campaign with its configuration."""

    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)

    # Agent identity
    agent_name = Column(String(100), nullable=False)
    company_name = Column(String(200), nullable=False)

    # Service being promoted
    service_name = Column(String(200), nullable=False)
    service_description = Column(Text, nullable=False)
    campaign_objective = Column(Text, nullable=False)

    # Call configuration
    language = Column(String(50), default="English")
    max_call_duration_seconds = Column(Integer, default=300)
    retry_attempts = Column(Integer, default=3)
    retry_interval_hours = Column(Integer, default=24)

    # Questions to ask — stored as JSON array
    # Format: [{"id": "q1", "text": "Question text..."}, ...]
    questions = Column(JSONB, nullable=False, default=list)

    # Voice configuration
    voice_id = Column(String(200), nullable=True)
    tone = Column(String(50), default="professional_warm")

    # Campaign status
    status = Column(
        Enum(CampaignStatus),
        default=CampaignStatus.DRAFT,
        nullable=False,
    )

    # Stats (denormalized for quick access)
    total_contacts = Column(Integer, default=0)
    calls_completed = Column(Integer, default=0)
    calls_interested = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    contacts = relationship("Contact", back_populates="campaign", lazy="selectin")
    call_sessions = relationship("CallSession", back_populates="campaign", lazy="selectin")

    def __repr__(self):
        return f"<Campaign(id={self.id}, name='{self.name}', status='{self.status}')>"
