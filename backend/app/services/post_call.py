# ============================================================
# Post-Call Extraction Service
# File: app/services/post_call.py
#
# Processes call transcripts through GPT-4.1 to extract
# structured JSON data for Excel report population.
# ============================================================

import json
import logging
from datetime import datetime

from openai import OpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.call_session import CallSession, CallOutcome, Sentiment
from app.models.call_log import CallLog
from app.models.campaign import Campaign
from app.models.contact import Contact

logger = logging.getLogger(__name__)
settings = get_settings()


class PostCallProcessor:
    """Extracts structured data from call transcripts using GPT-4.1."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = OpenAI(api_key=settings.openai_api_key)

    async def process(self, session_id: int) -> dict:
        """
        Run post-call extraction on a completed call session.

        Args:
            session_id: Database ID of the CallSession

        Returns:
            Extracted data dict
        """
        # Load session, campaign, and contact
        session = await self.db.get(CallSession, session_id)
        if not session:
            logger.error(f"CallSession {session_id} not found")
            return {}

        campaign = await self.db.get(Campaign, session.campaign_id)
        contact = await self.db.get(Contact, session.contact_id)

        if not campaign or not contact:
            logger.error(f"Campaign or Contact not found for session {session_id}")
            return {}

        transcript = session.transcript
        if not transcript:
            logger.warning(f"No transcript for session {session_id}")
            # Set as incomplete
            session.call_outcome = CallOutcome.INCOMPLETE
            return {}

        # Build extraction prompt
        from app.prompts.post_call_extraction import build_extraction_prompt

        extraction_prompt = build_extraction_prompt(
            transcript=transcript,
            campaign=campaign,
            client_name=contact.client_name,
            phone_number=contact.phone_number,
            call_duration=session.duration_seconds or 0,
        )

        # Call GPT-4.1 for extraction
        try:
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a data extraction specialist. "
                            "Extract structured data from call transcripts. "
                            "Return ONLY valid JSON. No explanation, no markdown."
                        ),
                    },
                    {"role": "user", "content": extraction_prompt},
                ],
                temperature=0.1,
                max_tokens=2000,
                response_format={"type": "json_object"},
            )

            raw_response = response.choices[0].message.content.strip()

            # Parse JSON
            extracted_data = json.loads(raw_response)
            logger.info(f"Extraction successful for session {session_id}")

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error for session {session_id}: {e}")
            extracted_data = {}
        except Exception as e:
            logger.error(f"LLM extraction error for session {session_id}: {e}")
            extracted_data = {}

        # Update session with extracted data
        await self._update_session(session, extracted_data)

        # Log the extraction event
        log = CallLog(
            session_id=session.session_id,
            event_type="extraction_completed",
            event_data={
                "fields_extracted": len(extracted_data),
                "has_outcome": extracted_data.get("call_outcome") is not None,
            },
        )
        self.db.add(log)

        # Update campaign stats
        await self._update_campaign_stats(campaign, extracted_data)

        return extracted_data

    async def _update_session(self, session: CallSession, data: dict):
        """Update the CallSession with extracted data."""
        session.extracted_data = data

        # Map call outcome
        outcome = data.get("call_outcome")
        if outcome:
            try:
                session.call_outcome = CallOutcome(outcome)
            except ValueError:
                session.call_outcome = CallOutcome.INCOMPLETE

        # Map sentiment
        sentiment = data.get("sentiment")
        if sentiment:
            try:
                session.sentiment = Sentiment(sentiment)
            except ValueError:
                session.sentiment = Sentiment.NEUTRAL

        # Denormalized fields
        session.preferred_callback_time = data.get("preferred_callback_time")
        session.email_requested = data.get("email_requested", False)
        session.demo_requested = data.get("demo_requested", False)
        session.objections_raised = data.get("objections_raised", [])
        session.additional_notes = data.get("additional_notes", "")

        # Question answers
        question_answers = {}
        for key, value in data.items():
            if key.startswith("question_") and key.endswith("_answer"):
                question_answers[key] = value
        session.question_answers = question_answers

    async def _update_campaign_stats(self, campaign: Campaign, data: dict):
        """Update denormalized campaign statistics."""
        campaign.calls_completed = (campaign.calls_completed or 0) + 1

        if data.get("call_outcome") == "interested":
            campaign.calls_interested = (campaign.calls_interested or 0) + 1
