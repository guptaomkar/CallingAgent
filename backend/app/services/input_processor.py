# ============================================================
# Input Processor Service
# File: app/services/input_processor.py
#
# Reads and validates client contact lists from Excel/CSV,
# applies E.164 phone validation, deduplication, and DND checks.
# ============================================================

import io
import logging
from typing import Optional

import pandas as pd
import phonenumbers
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import Contact, ContactStatus
from app.schemas.contact import ContactUploadResponse

logger = logging.getLogger(__name__)


class InputProcessor:
    """Processes uploaded contact files for a campaign."""

    # Required columns in the input file
    REQUIRED_COLUMNS = {"client_name", "phone_number"}

    # Optional columns
    OPTIONAL_COLUMNS = {"email", "preferred_language", "notes", "last_contacted"}

    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_file(
        self,
        file_content: bytes,
        filename: str,
        campaign_id: int,
        default_country: str = "IN",
    ) -> ContactUploadResponse:
        """
        Process an uploaded Excel/CSV file and import validated contacts.

        Args:
            file_content: Raw bytes of the uploaded file
            filename: Original filename (for format detection)
            campaign_id: Campaign to associate contacts with
            default_country: Default country code for phone parsing

        Returns:
            ContactUploadResponse with import statistics
        """
        # Parse file into DataFrame
        df = self._parse_file(file_content, filename)

        total_rows = len(df)
        valid_count = 0
        duplicate_count = 0
        invalid_count = 0
        dnd_count = 0
        errors = []

        # Normalize column names
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

        # Check required columns
        missing = self.REQUIRED_COLUMNS - set(df.columns)
        if missing:
            return ContactUploadResponse(
                total_rows=total_rows,
                valid_contacts=0,
                duplicates_skipped=0,
                invalid_rows=total_rows,
                dnd_excluded=0,
                errors=[{"row": 0, "error": f"Missing required columns: {missing}"}],
            )

        # Get existing phone numbers for deduplication
        existing_phones = await self._get_existing_phones(campaign_id)

        # Process each row
        contacts_to_add = []
        for idx, row in df.iterrows():
            row_num = idx + 2  # Account for header row and 0-indexing

            try:
                # Validate and normalize phone number
                phone = self._validate_phone(
                    str(row.get("phone_number", "")),
                    default_country,
                )
                if not phone:
                    invalid_count += 1
                    errors.append({
                        "row": row_num,
                        "error": f"Invalid phone number: {row.get('phone_number', '')}",
                    })
                    continue

                # Check for duplicates
                if phone in existing_phones:
                    duplicate_count += 1
                    continue

                # Get client name
                client_name = str(row.get("client_name", "")).strip()
                if not client_name:
                    invalid_count += 1
                    errors.append({
                        "row": row_num,
                        "error": "Missing client name",
                    })
                    continue

                # Build contact
                contact = Contact(
                    campaign_id=campaign_id,
                    client_name=client_name,
                    phone_number=phone,
                    email=self._clean_field(row.get("email")),
                    preferred_language=self._clean_field(row.get("preferred_language")),
                    notes=self._clean_field(row.get("notes")),
                    status=ContactStatus.PENDING,
                )

                contacts_to_add.append(contact)
                existing_phones.add(phone)
                valid_count += 1

            except Exception as e:
                invalid_count += 1
                errors.append({
                    "row": row_num,
                    "error": str(e),
                })

        # Bulk insert valid contacts
        if contacts_to_add:
            self.db.add_all(contacts_to_add)
            await self.db.flush()
            logger.info(
                f"Imported {valid_count} contacts for campaign {campaign_id}"
            )

        return ContactUploadResponse(
            total_rows=total_rows,
            valid_contacts=valid_count,
            duplicates_skipped=duplicate_count,
            invalid_rows=invalid_count,
            dnd_excluded=dnd_count,
            errors=errors[:50],  # Cap errors at 50
        )

    def _parse_file(self, content: bytes, filename: str) -> pd.DataFrame:
        """Parse file content into a pandas DataFrame."""
        buffer = io.BytesIO(content)

        if filename.endswith(".csv"):
            return pd.read_csv(buffer, dtype=str).fillna("")
        elif filename.endswith(".xlsx"):
            return pd.read_excel(buffer, dtype=str, engine="openpyxl").fillna("")
        else:
            raise ValueError(f"Unsupported file format: {filename}")

    def _validate_phone(self, phone_str: str, default_country: str = "IN") -> Optional[str]:
        """
        Validate and normalize a phone number to E.164 format.

        Args:
            phone_str: Raw phone number string
            default_country: Default country code (ISO 3166-1 alpha-2)

        Returns:
            E.164 formatted phone number or None if invalid
        """
        phone_str = phone_str.strip()
        if not phone_str:
            return None

        try:
            parsed = phonenumbers.parse(phone_str, default_country)
            if phonenumbers.is_valid_number(parsed):
                return phonenumbers.format_number(
                    parsed,
                    phonenumbers.PhoneNumberFormat.E164,
                )
        except phonenumbers.NumberParseException:
            pass

        return None

    async def _get_existing_phones(self, campaign_id: int) -> set:
        """Get all existing phone numbers for deduplication."""
        result = await self.db.execute(
            select(Contact.phone_number).where(
                Contact.campaign_id == campaign_id
            )
        )
        return {row[0] for row in result.fetchall()}

    @staticmethod
    def _clean_field(value) -> Optional[str]:
        """Clean a field value — return None for empty/NaN."""
        if pd.isna(value) or str(value).strip() == "":
            return None
        return str(value).strip()
