# ============================================================
# LangGraph Call State Definition
# File: app/graph/state.py
#
# Defines the TypedDict state that flows through the
# LangGraph state machine during a call session.
# ============================================================

from typing import Annotated, Optional
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages


class CallState(TypedDict):
    """
    State object that flows through the LangGraph call flow.
    Each field represents a piece of the call's current state.
    """

    # --- Session Identity ---
    session_id: str
    contact: dict          # Client contact info (name, phone, email, etc.)
    campaign: dict         # Full campaign config (agent_name, company, questions, etc.)

    # --- Conversation ---
    messages: Annotated[list, add_messages]  # LangChain message history
    current_turn: int                         # Current conversation turn number

    # --- Question Tracking ---
    current_question_index: int    # Index of the next question to ask (0-based)
    total_questions: int           # Total number of questions in the campaign
    questions_answered: dict       # {question_id: answer_text}

    # --- Call Flow State ---
    call_phase: str                 # greeting | consent | questioning | objection | closing | voicemail | post_call
    consent_given: Optional[bool]   # Whether client agreed to proceed
    objection_detected: bool        # Whether an objection was detected in last response
    last_objection: Optional[str]   # The objection text if detected

    # --- Outcomes ---
    call_outcome: Optional[str]     # interested | not_interested | callback_requested | voicemail | no_answer | incomplete
    sentiment: Optional[str]        # positive | neutral | negative
    callback_requested: bool
    preferred_callback_time: Optional[str]
    email_requested: bool
    demo_requested: bool
    objections_raised: list         # List of all objections raised during call

    # --- Metadata ---
    call_status: str                # initiated | connected | in_progress | completed | failed
    error: Optional[str]            # Error message if something went wrong
    additional_notes: str           # Any extra notes captured during the call
