# ============================================================
# DND (Do Not Disturb) Checker Service
# File: app/services/dnd_checker.py
#
# Validates phone numbers against DND/blacklist before calling.
# Auto-blacklists contacts who opt out.
# ============================================================

import logging
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import Contact, ContactStatus

logger = logging.getLogger(__name__)


class DNDChecker:
    """
    Checks contacts against DND lists and manages blacklisting.

    Supports:
    - Internal blacklist (contacts who said "not interested" / "remove me")
    - DND flag checking before each call
    - Bulk DND list import from CSV
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def is_blocked(self, phone_number: str) -> bool:
        """
        Check if a phone number is on DND or blacklisted.

        Args:
            phone_number: E.164 formatted phone number

        Returns:
            True if the number should NOT be called
        """
        result = await self.db.execute(
            select(Contact).where(
                Contact.phone_number == phone_number,
                (Contact.is_dnd == True) | (Contact.is_blacklisted == True),
            )
        )
        blocked = result.scalar_one_or_none()
        return blocked is not None

    async def blacklist_contact(self, contact_id: int, reason: str = "opt_out"):
        """
        Add a contact to the blacklist.
        Called when a contact says "not interested" or "remove me".

        Args:
            contact_id: Contact database ID
            reason: Reason for blacklisting
        """
        contact = await self.db.get(Contact, contact_id)
        if contact:
            contact.is_blacklisted = True
            contact.status = ContactStatus.BLACKLISTED
            contact.notes = f"{contact.notes or ''}\n[BLACKLISTED: {reason}]".strip()
            logger.info(f"Contact {contact_id} blacklisted: {reason}")

    async def blacklist_phone(self, phone_number: str, reason: str = "opt_out"):
        """
        Blacklist all contacts with a specific phone number.

        Args:
            phone_number: E.164 phone number to blacklist
            reason: Reason for blacklisting
        """
        await self.db.execute(
            update(Contact)
            .where(Contact.phone_number == phone_number)
            .values(
                is_blacklisted=True,
                status=ContactStatus.BLACKLISTED,
            )
        )
        logger.info(f"Phone number {phone_number} blacklisted across all campaigns")

    async def mark_dnd(self, phone_number: str):
        """Mark a phone number as DND across all campaigns."""
        await self.db.execute(
            update(Contact)
            .where(Contact.phone_number == phone_number)
            .values(
                is_dnd=True,
                status=ContactStatus.DND,
            )
        )
        logger.info(f"Phone number {phone_number} marked as DND")

    async def import_dnd_list(self, phone_numbers: list[str]) -> int:
        """
        Import a list of DND phone numbers.

        Args:
            phone_numbers: List of E.164 phone numbers

        Returns:
            Number of contacts marked as DND
        """
        count = 0
        for phone in phone_numbers:
            phone = phone.strip()
            if phone:
                result = await self.db.execute(
                    update(Contact)
                    .where(Contact.phone_number == phone)
                    .values(is_dnd=True, status=ContactStatus.DND)
                )
                count += result.rowcount

        logger.info(f"DND import: {count} contacts marked")
        return count

    async def check_and_filter_contacts(
        self,
        campaign_id: int,
    ) -> list[Contact]:
        """
        Get all callable contacts for a campaign (excluding DND/blacklisted).

        Args:
            campaign_id: Campaign ID

        Returns:
            List of contacts that can be called
        """
        result = await self.db.execute(
            select(Contact).where(
                Contact.campaign_id == campaign_id,
                Contact.status == ContactStatus.PENDING,
                Contact.is_dnd == False,
                Contact.is_blacklisted == False,
            ).order_by(Contact.created_at.asc())
        )
        return list(result.scalars().all())
