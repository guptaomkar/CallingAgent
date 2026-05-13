# ============================================================
# Telephony Service — Vapi.ai Integration
# File: app/services/telephony.py
#
# Manages outbound call initiation and session management
# via Vapi.ai API (primary) or Twilio (fallback).
# ============================================================

import logging
from typing import Optional

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class TelephonyService:
    """Manages outbound calling via Vapi.ai or Twilio."""

    def __init__(self):
        self.vapi_base_url = settings.vapi_base_url
        self.vapi_api_key = settings.vapi_api_key
        self.vapi_phone_number_id = settings.vapi_phone_number_id

    async def initiate_call(
        self,
        phone_number: str,
        session_id: str,
        campaign_id: int,
        contact_id: int,
        assistant_config: Optional[dict] = None,
    ) -> dict:
        """
        Initiate an outbound call via Vapi.ai.

        Args:
            phone_number: E.164 formatted phone number to call
            session_id: Our internal session UUID
            campaign_id: Campaign ID for metadata
            contact_id: Contact ID for metadata
            assistant_config: Optional override for assistant configuration

        Returns:
            dict with provider_call_id and status
        """
        try:
            payload = {
                "phoneNumberId": self.vapi_phone_number_id,
                "customer": {
                    "number": phone_number,
                },
                "metadata": {
                    "session_id": session_id,
                    "campaign_id": str(campaign_id),
                    "contact_id": str(contact_id),
                },
                # Use server URL for dynamic assistant configuration
                "assistantOverrides": assistant_config or {},
                "serverUrl": f"{settings.app_host}:{settings.app_port}/api/v1/webhooks/vapi",
            }

            # If no assistant overrides, use the webhook-based assistant-request flow
            if not assistant_config:
                payload["server"] = {
                    "url": f"https://your-server.com/api/v1/webhooks/vapi",
                    "timeoutSeconds": 20,
                }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.vapi_base_url}/call",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.vapi_api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=30.0,
                )

                if response.status_code == 201:
                    data = response.json()
                    provider_call_id = data.get("id", "")
                    logger.info(
                        f"Vapi call initiated: {provider_call_id} → {phone_number}"
                    )
                    return {
                        "success": True,
                        "provider_call_id": provider_call_id,
                        "status": "initiated",
                        "provider": "vapi",
                    }
                else:
                    error_msg = response.text
                    logger.error(
                        f"Vapi call failed ({response.status_code}): {error_msg}"
                    )
                    return {
                        "success": False,
                        "error": error_msg,
                        "status": "failed",
                        "provider": "vapi",
                    }

        except Exception as e:
            logger.error(f"Telephony error: {e}")
            return {
                "success": False,
                "error": str(e),
                "status": "failed",
                "provider": "vapi",
            }

    async def end_call(self, provider_call_id: str) -> dict:
        """
        End an active call via Vapi.ai.

        Args:
            provider_call_id: The Vapi call ID to end

        Returns:
            Result dict
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.vapi_base_url}/call/{provider_call_id}",
                    headers={
                        "Authorization": f"Bearer {self.vapi_api_key}",
                    },
                    timeout=15.0,
                )

                if response.status_code in (200, 204):
                    logger.info(f"Call ended: {provider_call_id}")
                    return {"success": True}
                else:
                    return {"success": False, "error": response.text}

        except Exception as e:
            logger.error(f"Error ending call: {e}")
            return {"success": False, "error": str(e)}

    async def get_call_status(self, provider_call_id: str) -> dict:
        """
        Get current status of a call from Vapi.ai.

        Args:
            provider_call_id: The Vapi call ID

        Returns:
            Call status dict
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.vapi_base_url}/call/{provider_call_id}",
                    headers={
                        "Authorization": f"Bearer {self.vapi_api_key}",
                    },
                    timeout=15.0,
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": response.text}

        except Exception as e:
            logger.error(f"Error getting call status: {e}")
            return {"error": str(e)}


class TwilioFallbackService:
    """
    Fallback telephony via Twilio Programmable Voice.
    Used when Vapi.ai is unavailable or for specific use cases.
    """

    def __init__(self):
        self.account_sid = settings.twilio_account_sid
        self.auth_token = settings.twilio_auth_token
        self.phone_number = settings.twilio_phone_number

    async def initiate_call(
        self,
        phone_number: str,
        session_id: str,
        webhook_url: str,
    ) -> dict:
        """Initiate a call via Twilio."""
        try:
            from twilio.rest import Client

            client = Client(self.account_sid, self.auth_token)

            call = client.calls.create(
                to=phone_number,
                from_=self.phone_number,
                url=webhook_url,
                status_callback=f"{webhook_url}/status",
                status_callback_event=["initiated", "ringing", "answered", "completed"],
                record=True,
                machine_detection="Enable",
            )

            logger.info(f"Twilio call initiated: {call.sid} → {phone_number}")
            return {
                "success": True,
                "provider_call_id": call.sid,
                "status": "initiated",
                "provider": "twilio",
            }

        except Exception as e:
            logger.error(f"Twilio error: {e}")
            return {
                "success": False,
                "error": str(e),
                "status": "failed",
                "provider": "twilio",
            }
