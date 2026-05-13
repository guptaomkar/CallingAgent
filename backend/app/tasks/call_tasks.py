# ============================================================
# Call Execution Tasks (Celery)
# File: app/tasks/call_tasks.py
#
# Background tasks for executing individual calls,
# post-call processing, and retry scheduling.
# ============================================================

import asyncio
import logging

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Helper to run async code in a sync Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(
    name="app.tasks.call_tasks.execute_single_call",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    queue="calls",
)
def execute_single_call(self, session_id: int):
    """
    Execute a single outbound call.

    This task:
    1. Loads the CallSession from DB
    2. Runs pre-call checks (DND, blacklist)
    3. Initiates the call via Vapi.ai
    4. The actual conversation is handled by Vapi + our webhook

    Args:
        session_id: Database ID of the CallSession
    """
    logger.info(f"[Task] Executing call for session {session_id}")

    async def _execute():
        from app.database import async_session_factory
        from app.services.call_orchestrator import CallOrchestrator

        async with async_session_factory() as db:
            orchestrator = CallOrchestrator(db)
            result = await orchestrator.execute_call(session_id)
            await db.commit()
            return result

    try:
        result = _run_async(_execute())

        if not result.get("success", False):
            error = result.get("error", "Unknown error")
            logger.warning(f"[Task] Call failed for session {session_id}: {error}")

            # Retry on transient errors
            if "timeout" in error.lower() or "connection" in error.lower():
                raise self.retry(exc=Exception(error))

        return result

    except Exception as e:
        logger.error(f"[Task] Call execution error for session {session_id}: {e}")
        raise


@celery_app.task(
    name="app.tasks.call_tasks.process_post_call",
    queue="calls",
)
def process_post_call(session_id: int):
    """
    Run post-call processing for a completed call.

    This task:
    1. Loads the full transcript
    2. Sends it to GPT-4.1 for extraction (Prompt 5)
    3. Updates the CallSession with extracted data
    4. Updates campaign statistics
    5. Checks for opt-out and blacklisting

    Args:
        session_id: Database ID of the CallSession
    """
    logger.info(f"[Task] Post-call processing for session {session_id}")

    async def _process():
        from app.database import async_session_factory
        from app.services.call_orchestrator import CallOrchestrator

        async with async_session_factory() as db:
            orchestrator = CallOrchestrator(db)
            await orchestrator.handle_call_completed(session_id)
            await db.commit()

    try:
        _run_async(_process())
        logger.info(f"[Task] Post-call processing complete for session {session_id}")
    except Exception as e:
        logger.error(f"[Task] Post-call error for session {session_id}: {e}")
        raise


@celery_app.task(
    name="app.tasks.call_tasks.schedule_retry_call",
    queue="calls",
)
def schedule_retry_call(contact_id: int, campaign_id: int):
    """
    Create a new call session and execute a retry call.

    Args:
        contact_id: Contact to retry
        campaign_id: Campaign the contact belongs to
    """
    logger.info(f"[Task] Retry call for contact {contact_id}, campaign {campaign_id}")

    async def _retry():
        from app.database import async_session_factory
        from app.models.call_session import CallSession, CallStatus
        from app.services.call_orchestrator import CallOrchestrator

        async with async_session_factory() as db:
            # Create a new session for the retry
            session = CallSession(
                contact_id=contact_id,
                campaign_id=campaign_id,
                call_status=CallStatus.INITIATED,
                is_retry=True,
            )
            db.add(session)
            await db.flush()
            await db.refresh(session)

            # Execute the call
            orchestrator = CallOrchestrator(db)
            result = await orchestrator.execute_call(session.id)
            await db.commit()
            return result

    try:
        result = _run_async(_retry())
        return result
    except Exception as e:
        logger.error(f"[Task] Retry call error: {e}")
        raise
