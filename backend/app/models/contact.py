# ============================================================
# Contact ORM Model
# File: app/models/contact.py
# ============================================================

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class ContactStatus(str, enum.Enum):
    PENDING = "pending"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    DND = "dnd"
    BLACKLISTED = "blacklisted"


class Contact(Base):
    """Represents a client contact to be called."""

    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Campaign linkage
    campaign_id = Column(
        Integer,
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Contact info
    client_name = Column(String(200), nullable=False)
    phone_number = Column(String(20), nullable=False, index=True)
    email = Column(String(200), nullable=True)

    # Call preferences
    preferred_language = Column(String(50), nullable=True)
    preferred_callback_time = Column(String(100), nullable=True)

    # Contact status
    status = Column(
        Enum(ContactStatus),
        default=ContactStatus.PENDING,
        nullable=False,
        index=True,
    )

    # DND / Blacklist
    is_dnd = Column(Boolean, default=False)
    is_blacklisted = Column(Boolean, default=False)

    # Call tracking
    last_contacted = Column(DateTime, nullable=True)
    retry_count = Column(Integer, default=0)

    # Pre-call notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    campaign = relationship("Campaign", back_populates="contacts")
    call_sessions = relationship("CallSession", back_populates="contact", lazy="selectin")

    def __repr__(self):
        return f"<Contact(id={self.id}, name='{self.client_name}', phone='{self.phone_number}')>"
