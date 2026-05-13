# ============================================================
# Call Log ORM Model
# File: app/models/call_log.py
# ============================================================

from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.database import Base


class CallLog(Base):
    """Granular event log for each call session — used for audit and debugging."""

    __tablename__ = "call_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Link to call session
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("call_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Event info
    event_type = Column(String(50), nullable=False, index=True)
    # Event types: call_initiated, call_ringing, call_connected,
    # agent_spoke, client_spoke, question_asked, answer_received,
    # objection_detected, objection_handled, consent_given,
    # consent_denied, call_ended, extraction_completed,
    # report_written, retry_scheduled, error

    event_data = Column(JSONB, nullable=True)
    # Flexible payload for each event type

    # Timestamp
    timestamp = Column(DateTime, server_default=func.now(), index=True)

    # Relationships
    call_session = relationship("CallSession", back_populates="call_logs")

    def __repr__(self):
        return f"<CallLog(id={self.id}, event='{self.event_type}', time='{self.timestamp}')>"
