# ============================================================
# Batch Call Tasks (Celery)
# File: app/tasks/batch_tasks.py
#
# Orchestrates batch calling campaigns — queues contacts,
# manages concurrency, and tracks campaign progress.
# ============================================================

import asyncio
import logging
import time

from celery import group

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
    name="app.tasks.batch_tasks.launch_campaign",
    queue="default",
)
def launch_campaign(campaign_id: int, max_concurrent: int = 10):
    """
    Launch a batch calling campaign.

    This task:
    1. Loads all pending contacts for the campaign
    2. Filters out DND/blacklisted contacts
    3. Creates CallSession entries for each contact
    4. Dispatches call tasks in batches respecting concurrency limits

    Args:
        campaign_id: Campaign to launch
        max_concurrent: Maximum concurrent calls
    """
    logger.info(
        f"[Batch] Launching campaign {campaign_id} "
        f"(max concurrent: {max_concurrent})"
    )

    async def _launch():
        from app.database import async_session_factory
        from app.models.call_session import CallSession, CallStatus
        from app.models.campaign import Campaign, CampaignStatus
        from app.models.contact import Contact, ContactStatus
        from app.services.dnd_checker import DNDChecker
        from sqlalchemy import select

        async with async_session_factory() as db:
            # Load campaign
            campaign = await db.get(Campaign, campaign_id)
            if not campaign:
                logger.error(f"Campaign {campaign_id} not found")
                return {"error": "Campaign not found"}

            # Update campaign status
            campaign.status = CampaignStatus.ACTIVE

            # Get callable contacts
            dnd_checker = DNDChecker(db)
            contacts = await dnd_checker.check_and_filter_contacts(campaign_id)

            if not contacts:
                logger.warning(f"No callable contacts for campaign {campaign_id}")
                return {"error": "No contacts to call"}

            logger.info(f"[Batch] {len(contacts)} contacts ready for campaign {campaign_id}")

            # Update campaign stats
            campaign.total_contacts = len(contacts)

            # Create call sessions for all contacts
            sessions = []
            for contact in contacts:
                session = CallSession(
                    contact_id=contact.id,
                    campaign_id=campaign_id,
                    call_status=CallStatus.INITIATED,
                )
                db.add(session)
                sessions.append(session)

            await db.flush()

            # Refresh to get IDs
            session_ids = []
            for session in sessions:
                await db.refresh(session)
                session_ids.append(session.id)

            await db.commit()

            return {
                "campaign_id": campaign_id,
                "total_contacts": len(contacts),
                "session_ids": session_ids,
            }

    try:
        result = _run_async(_launch())

        if "error" in result:
            return result

        session_ids = result.get("session_ids", [])
        total = len(session_ids)

        logger.info(f"[Batch] Dispatching {total} calls in batches of {max_concurrent}")

        # Dispatch calls in batches
        from app.tasks.call_tasks import execute_single_call

        for batch_start in range(0, total, max_concurrent):
            batch = session_ids[batch_start : batch_start + max_concurrent]
            batch_num = (batch_start // max_concurrent) + 1

            logger.info(
                f"[Batch] Dispatching batch {batch_num} "
                f"({len(batch)} calls, {batch_start+1}-{batch_start+len(batch)}/{total})"
            )

            # Create a group of tasks for this batch
            task_group = group(
                execute_single_call.s(sid) for sid in batch
            )
            task_group.apply_async()

            # Wait between batches to avoid overwhelming the telephony provider
            if batch_start + max_concurrent < total:
                # Wait for calls to complete before next batch
                # Average call duration ~3-5 min, add buffer
                wait_seconds = 30  # Minimum wait between batches
                logger.info(f"[Batch] Waiting {wait_seconds}s before next batch")
                time.sleep(wait_seconds)

        logger.info(f"[Batch] All {total} calls dispatched for campaign {campaign_id}")

        return {
            "campaign_id": campaign_id,
            "total_dispatched": total,
            "status": "dispatched",
        }

    except Exception as e:
        logger.error(f"[Batch] Campaign launch error: {e}")
        raise


@celery_app.task(
    name="app.tasks.batch_tasks.check_campaign_progress",
    queue="default",
)
def check_campaign_progress(campaign_id: int) -> dict:
    """
    Check the progress of a running campaign.

    Returns:
        Progress dict with counts for each status
    """
    async def _check():
        from app.database import async_session_factory
        from app.models.call_session import CallSession
        from sqlalchemy import select, func

        async with async_session_factory() as db:
            result = await db.execute(
                select(
                    CallSession.call_status,
                    func.count(CallSession.id),
                )
                .where(CallSession.campaign_id == campaign_id)
                .group_by(CallSession.call_status)
            )

            progress = {}
            for status, count in result:
                progress[status.value if hasattr(status, "value") else str(status)] = count

            return progress

    return _run_async(_check())
