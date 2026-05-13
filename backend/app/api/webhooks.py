# ============================================================
# Webhook Handlers — Vapi.ai & Twilio Callbacks
# File: app/api/webhooks.py
# ============================================================

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.call_session import CallSession, CallStatus, CallOutcome
from app.models.call_log import CallLog

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/vapi")
async def vapi_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle incoming webhooks from Vapi.ai.

    Vapi sends events like:
    - assistant-request: Agent needs configuration
    - call-started: Call has connected
    - call-ended: Call has ended
    - transcript: Real-time transcript update
    - hang: Call was hung up
    - speech-update: Agent/user speech events
    """
    body = await request.json()
    event_type = body.get("message", {}).get("type", "unknown")

    logger.info(f"Vapi webhook received: {event_type}")

    if event_type == "assistant-request":
        # Vapi is asking for assistant configuration
        # We return the system prompt and tools dynamically
        return await _handle_assistant_request(body, db)

    elif event_type == "call-started":
        await _handle_call_started(body, db)

    elif event_type == "call-ended":
        await _handle_call_ended(body, db)

    elif event_type == "transcript":
        await _handle_transcript_update(body, db)

    elif event_type == "end-of-call-report":
        await _handle_end_of_call_report(body, db)

    return {"status": "ok"}


async def _handle_assistant_request(body: dict, db: AsyncSession) -> dict:
    """
    Return dynamic assistant configuration when Vapi asks.
    This is where we inject our prompt system.
    """
    call_data = body.get("message", {}).get("call", {})
    metadata = call_data.get("metadata", {})
    campaign_id = metadata.get("campaign_id")
    contact_id = metadata.get("contact_id")

    if not campaign_id:
        logger.warning("Assistant request without campaign_id in metadata")
        return {"error": "Missing campaign_id"}

    from app.models.campaign import Campaign
    from app.models.contact import Contact
    from app.prompts.system_persona import build_system_prompt
    from app.prompts.call_opening import build_opening_prompt
    from app.prompts.question_flow import build_question_flow_prompt
    from app.prompts.objection_handling import build_objection_prompt

    campaign = await db.get(Campaign, int(campaign_id))
    contact = await db.get(Contact, int(contact_id)) if contact_id else None

    if not campaign:
        return {"error": "Campaign not found"}

    # Build the full system prompt by combining all prompt modules
    system_prompt = build_system_prompt(campaign, contact)
    opening_prompt = build_opening_prompt(campaign, contact)
    question_prompt = build_question_flow_prompt(campaign)
    objection_prompt = build_objection_prompt(campaign)

    full_prompt = f"{system_prompt}\n\n{question_prompt}\n\n{objection_prompt}"

    return {
        "assistant": {
            "model": {
                "provider": "openai",
                "model": "gpt-4.1",
                "systemMessage": full_prompt,
                "temperature": 0.7,
            },
            "voice": {
                "provider": "11labs",
                "voiceId": campaign.voice_id or "default",
                "stability": 0.5,
                "similarityBoost": 0.75,
            },
            "firstMessage": opening_prompt,
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-2",
                "language": campaign.language.lower() if campaign.language else "en",
            },
            "silenceTimeoutSeconds": 30,
            "maxDurationSeconds": campaign.max_call_duration_seconds,
            "endCallMessage": "Thank you for your time. Have a wonderful day! Goodbye.",
        }
    }


async def _handle_call_started(body: dict, db: AsyncSession):
    """Update call session when call connects."""
    call_data = body.get("message", {}).get("call", {})
    provider_call_id = call_data.get("id")
    metadata = call_data.get("metadata", {})
    session_id = metadata.get("session_id")

    if session_id:
        result = await db.execute(
            select(CallSession).where(CallSession.session_id == session_id)
        )
        session = result.scalar_one_or_none()
        if session:
            session.call_status = CallStatus.CONNECTED
            session.started_at = datetime.utcnow()
            session.provider_call_id = provider_call_id

            log = CallLog(
                session_id=session.session_id,
                event_type="call_connected",
                event_data={"provider_call_id": provider_call_id},
            )
            db.add(log)


async def _handle_call_ended(body: dict, db: AsyncSession):
    """Update call session when call ends and trigger post-call processing."""
    call_data = body.get("message", {}).get("call", {})
    metadata = call_data.get("metadata", {})
    session_id = metadata.get("session_id")

    if session_id:
        result = await db.execute(
            select(CallSession).where(CallSession.session_id == session_id)
        )
        session = result.scalar_one_or_none()
        if session:
            session.call_status = CallStatus.COMPLETED
            session.ended_at = datetime.utcnow()

            if session.started_at:
                duration = (session.ended_at - session.started_at).total_seconds()
                session.duration_seconds = int(duration)

            # Store recording URL if available
            recording_url = call_data.get("recordingUrl")
            if recording_url:
                session.recording_url = recording_url

            log = CallLog(
                session_id=session.session_id,
                event_type="call_ended",
                event_data={"duration": session.duration_seconds},
            )
            db.add(log)

            # Trigger post-call extraction
            from app.tasks.call_tasks import process_post_call

            process_post_call.delay(session.id)


async def _handle_transcript_update(body: dict, db: AsyncSession):
    """Store transcript updates in real-time."""
    call_data = body.get("message", {}).get("call", {})
    metadata = call_data.get("metadata", {})
    session_id = metadata.get("session_id")
    transcript = body.get("message", {}).get("transcript", "")

    if session_id and transcript:
        result = await db.execute(
            select(CallSession).where(CallSession.session_id == session_id)
        )
        session = result.scalar_one_or_none()
        if session:
            # Append to existing transcript
            existing = session.transcript or ""
            session.transcript = existing + "\n" + transcript


async def _handle_end_of_call_report(body: dict, db: AsyncSession):
    """Process the end-of-call report from Vapi with full transcript and summary."""
    call_data = body.get("message", {}).get("call", {})
    metadata = call_data.get("metadata", {})
    session_id = metadata.get("session_id")

    report = body.get("message", {})
    full_transcript = report.get("transcript", "")
    summary = report.get("summary", "")
    recording_url = report.get("recordingUrl", "")

    if session_id:
        result = await db.execute(
            select(CallSession).where(CallSession.session_id == session_id)
        )
        session = result.scalar_one_or_none()
        if session:
            session.transcript = full_transcript
            if recording_url:
                session.recording_url = recording_url

            log = CallLog(
                session_id=session.session_id,
                event_type="end_of_call_report",
                event_data={
                    "summary": summary,
                    "transcript_length": len(full_transcript),
                },
            )
            db.add(log)


@router.post("/twilio/status")
async def twilio_status_callback(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Handle Twilio status callback (fallback telephony provider)."""
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    call_status = form_data.get("CallStatus")

    logger.info(f"Twilio status callback: {call_sid} → {call_status}")

    # Map Twilio status to our internal status
    status_map = {
        "queued": CallStatus.INITIATED,
        "ringing": CallStatus.RINGING,
        "in-progress": CallStatus.IN_PROGRESS,
        "completed": CallStatus.COMPLETED,
        "busy": CallStatus.BUSY,
        "no-answer": CallStatus.NO_ANSWER,
        "failed": CallStatus.FAILED,
    }

    if call_sid:
        result = await db.execute(
            select(CallSession).where(CallSession.provider_call_id == call_sid)
        )
        session = result.scalar_one_or_none()
        if session:
            new_status = status_map.get(call_status)
            if new_status:
                session.call_status = new_status

            if call_status == "completed":
                session.ended_at = datetime.utcnow()
                duration = form_data.get("CallDuration")
                if duration:
                    session.duration_seconds = int(duration)

    return {"status": "ok"}
