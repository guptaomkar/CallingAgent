# ============================================================
# Call Session ORM Model
# File: app/models/call_session.py
# ============================================================

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.database import Base


class CallStatus(str, enum.Enum):
    INITIATED = "initiated"
    RINGING = "ringing"
    CONNECTED = "connected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NO_ANSWER = "no_answer"
    VOICEMAIL = "voicemail"
    BUSY = "busy"


class CallOutcome(str, enum.Enum):
    INTERESTED = "interested"
    NOT_INTERESTED = "not_interested"
    CALLBACK_REQUESTED = "callback_requested"
    VOICEMAIL = "voicemail"
    NO_ANSWER = "no_answer"
    INCOMPLETE = "incomplete"


class Sentiment(str, enum.Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class CallSession(Base):
    """Represents a single call attempt to a contact."""

    __tablename__ = "call_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        index=True,
    )

    # Linkages
    contact_id = Column(
        Integer,
        ForeignKey("contacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    campaign_id = Column(
        Integer,
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Call status tracking
    call_status = Column(
        Enum(CallStatus),
        default=CallStatus.INITIATED,
        nullable=False,
    )

    # Timing
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    # Retry info
    retry_count = Column(Integer, default=0)
    is_retry = Column(Boolean, default=False)

    # Telephony provider data
    provider_call_id = Column(String(200), nullable=True)  # Vapi/Twilio call ID
    recording_url = Column(String(500), nullable=True)

    # Conversation data
    transcript = Column(Text, nullable=True)
    conversation_history = Column(JSONB, nullable=True)  # Full message history

    # Extracted data (from Prompt 5)
    extracted_data = Column(JSONB, nullable=True)

    # Outcomes
    call_outcome = Column(Enum(CallOutcome), nullable=True)
    sentiment = Column(Enum(Sentiment), nullable=True)

    # Specific extracted fields (denormalized for quick queries)
    preferred_callback_time = Column(String(100), nullable=True)
    email_requested = Column(Boolean, default=False)
    demo_requested = Column(Boolean, default=False)
    objections_raised = Column(JSONB, nullable=True, default=list)
    additional_notes = Column(Text, nullable=True)

    # Question answers (denormalized)
    question_answers = Column(JSONB, nullable=True, default=dict)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    contact = relationship("Contact", back_populates="call_sessions")
    campaign = relationship("Campaign", back_populates="call_sessions")
    call_logs = relationship("CallLog", back_populates="call_session", lazy="selectin")

    def __repr__(self):
        return f"<CallSession(id={self.id}, session='{self.session_id}', status='{self.call_status}')>"
