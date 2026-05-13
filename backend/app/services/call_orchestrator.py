# ============================================================
# Call Orchestrator Service
# File: app/services/call_orchestrator.py
#
# The central service that manages a call session end-to-end:
# initializes the LangGraph state machine, coordinates with
# telephony, and triggers post-call processing.
# ============================================================

import logging
import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.call_session import CallSession, CallStatus
from app.models.call_log import CallLog
from app.models.campaign import Campaign
from app.models.contact import Contact, ContactStatus
from app.graph.builder import build_call_graph, create_initial_state
from app.services.telephony import TelephonyService
from app.services.dnd_checker import DNDChecker

logger = logging.getLogger(__name__)
settings = get_settings()


class CallOrchestrator:
    """
    Orchestrates a single call from initiation to completion.

    Responsibilities:
    - Creates the call session
    - Checks DND/blacklist
    - Initiates the call via telephony provider
    - Manages the LangGraph state machine
    - Triggers post-call processing
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.telephony = TelephonyService()
        self.dnd_checker = DNDChecker(db)

    async def execute_call(self, session_id: int) -> dict:
        """
        Execute a complete call for a given CallSession.

        Args:
            session_id: Database ID of the CallSession

        Returns:
            Call result dict with outcome and extracted data
        """
        # Load session
        session = await self.db.get(CallSession, session_id)
        if not session:
            logger.error(f"Session {session_id} not found")
            return {"error": "Session not found"}

        campaign = await self.db.get(Campaign, session.campaign_id)
        contact = await self.db.get(Contact, session.contact_id)

        if not campaign or not contact:
            session.call_status = CallStatus.FAILED
            return {"error": "Campaign or contact not found"}

        # Pre-call checks
        if contact.is_dnd or contact.is_blacklisted:
            session.call_status = CallStatus.FAILED
            await self._log_event(session, "call_blocked", {"reason": "DND/blacklisted"})
            return {"error": "Contact is DND or blacklisted"}

        if await self.dnd_checker.is_blocked(contact.phone_number):
            session.call_status = CallStatus.FAILED
            await self._log_event(session, "call_blocked", {"reason": "DND check failed"})
            return {"error": "Phone number is blocked"}

        # Update contact status
        contact.status = ContactStatus.IN_PROGRESS

        # Mark session as initiated
        session.call_status = CallStatus.INITIATED
        session.started_at = datetime.utcnow()
        await self._log_event(session, "call_initiated", {
            "phone": contact.phone_number,
            "campaign": campaign.campaign_id,
        })

        # Initiate call via Vapi.ai
        try:
            call_result = await self.telephony.initiate_call(
                phone_number=contact.phone_number,
                session_id=str(session.session_id),
                campaign_id=campaign.id,
                contact_id=contact.id,
            )

            if call_result.get("success"):
                session.provider_call_id = call_result.get("provider_call_id")
                session.call_status = CallStatus.RINGING
                await self._log_event(session, "call_ringing", call_result)

                logger.info(
                    f"Call initiated: {contact.client_name} ({contact.phone_number}) "
                    f"→ provider_id: {session.provider_call_id}"
                )

                return {
                    "success": True,
                    "session_id": str(session.session_id),
                    "provider_call_id": session.provider_call_id,
                    "status": "ringing",
                }
            else:
                session.call_status = CallStatus.FAILED
                await self._log_event(session, "call_failed", call_result)
                contact.status = ContactStatus.FAILED

                return {
                    "success": False,
                    "error": call_result.get("error", "Unknown error"),
                }

        except Exception as e:
            logger.error(f"Call execution error: {e}")
            session.call_status = CallStatus.FAILED
            contact.status = ContactStatus.FAILED
            await self._log_event(session, "error", {"error": str(e)})
            return {"success": False, "error": str(e)}

    async def handle_call_completed(self, session_id: int):
        """
        Handle post-call processing after a call ends.
        Called by webhook handler or Celery task.
        """
        session = await self.db.get(CallSession, session_id)
        if not session:
            return

        contact = await self.db.get(Contact, session.contact_id)

        # Update contact status
        if contact:
            contact.status = ContactStatus.COMPLETED
            contact.last_contacted = datetime.utcnow()
            contact.retry_count = (contact.retry_count or 0) + 1

        # Run post-call extraction
        from app.services.post_call import PostCallProcessor

        processor = PostCallProcessor(self.db)
        extracted_data = await processor.process(session_id)

        # Handle opt-out / blacklisting
        outcome = extracted_data.get("call_outcome", "")
        if outcome == "not_interested" and contact:
            # Check if they explicitly asked to be removed
            notes = extracted_data.get("additional_notes", "").lower()
            objections = [o.lower() for o in extracted_data.get("objections_raised", [])]
            if any(
                phrase in notes or any(phrase in o for o in objections)
                for phrase in ["remove", "stop calling", "don't call", "unsubscribe"]
            ):
                await self.dnd_checker.blacklist_contact(
                    contact.id,
                    reason="Client requested removal",
                )

        logger.info(f"Post-call processing complete for session {session.session_id}")

    async def schedule_retry(self, session_id: int) -> bool:
        """
        Schedule a retry call for a no-answer or voicemail session.

        Returns:
            True if retry was scheduled, False if max retries exceeded
        """
        session = await self.db.get(CallSession, session_id)
        if not session:
            return False

        campaign = await self.db.get(Campaign, session.campaign_id)
        contact = await self.db.get(Contact, session.contact_id)

        if not campaign or not contact:
            return False

        max_retries = campaign.retry_attempts or 3

        if (contact.retry_count or 0) >= max_retries:
            logger.info(
                f"Max retries ({max_retries}) reached for contact {contact.id}"
            )
            contact.status = ContactStatus.FAILED
            return False

        # Schedule retry via Celery delayed task
        retry_hours = campaign.retry_interval_hours or 24

        from app.tasks.call_tasks import schedule_retry_call

        schedule_retry_call.apply_async(
            args=[contact.id, campaign.id],
            countdown=retry_hours * 3600,  # Convert hours to seconds
        )

        await self._log_event(session, "retry_scheduled", {
            "retry_in_hours": retry_hours,
            "current_retry": contact.retry_count,
            "max_retries": max_retries,
        })

        logger.info(
            f"Retry scheduled for contact {contact.id} in {retry_hours}h "
            f"(attempt {contact.retry_count + 1}/{max_retries})"
        )
        return True

    async def _log_event(self, session: CallSession, event_type: str, data: dict):
        """Create a call log entry."""
        log = CallLog(
            session_id=session.session_id,
            event_type=event_type,
            event_data=data,
        )
        self.db.add(log)
