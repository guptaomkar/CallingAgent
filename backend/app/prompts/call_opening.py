# ============================================================
# Prompt 2 — Call Opening Script
# File: app/prompts/call_opening.py
#
# Injected as the first message when the call connects.
# The agent introduces itself and asks for consent to proceed.
# ============================================================

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.campaign import Campaign
    from app.models.contact import Contact


CALL_OPENING_TEMPLATE = """Hello, am I speaking with {client_name}?

Hi {client_name}! This is {agent_name} calling from {company_name}. I hope I've caught you at a good time — this will just take about 2 to 3 minutes of your time.

I'm reaching out today because {brief_reason}.

Would you be okay if I asked you a couple of quick questions? It'll help me understand how we can best serve you."""


VOICEMAIL_TEMPLATE = """Hi, this is {agent_name} from {company_name}. I was calling to share something that may be valuable for you. Please call us back or we'll try you again soon. Have a wonderful day!"""


BUSY_RESPONSE_TEMPLATE = """Absolutely, no problem at all! I completely respect that. Could I perhaps call back at a better time? When would work best for you?"""


def build_opening_prompt(campaign: Campaign, contact: Contact | None = None) -> str:
    """
    Build the call opening message — the first thing the agent says.

    Args:
        campaign: Campaign configuration
        contact: Client contact info for personalization

    Returns:
        The opening script string
    """
    client_name = contact.client_name if contact else "there"

    brief_reason = (
        f"we recently launched {campaign.service_name} and I believe it could "
        f"be really valuable for you"
    )

    return CALL_OPENING_TEMPLATE.format(
        client_name=client_name,
        agent_name=campaign.agent_name,
        company_name=campaign.company_name,
        brief_reason=brief_reason,
    )


def build_voicemail_message(campaign: Campaign) -> str:
    """Build the voicemail message to leave if no one answers."""
    return VOICEMAIL_TEMPLATE.format(
        agent_name=campaign.agent_name,
        company_name=campaign.company_name,
    )
