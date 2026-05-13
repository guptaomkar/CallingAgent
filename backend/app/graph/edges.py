# ============================================================
# LangGraph Conditional Edges
# File: app/graph/edges.py
#
# Defines routing logic between nodes based on call state.
# ============================================================

from app.graph.state import CallState


def route_after_greeting(state: CallState) -> str:
    """Route after the greeting node."""
    return "consent_check"


def route_after_consent(state: CallState) -> str:
    """
    Route based on consent check result.
    - consent → questioning
    - busy → closing (callback)
    - voicemail → voicemail
    - not interested → closing
    """
    call_phase = state.get("call_phase", "")
    consent = state.get("consent_given")

    if call_phase == "voicemail":
        return "voicemail"
    elif consent is True:
        return "question"
    else:
        return "closing"


def route_after_answer(state: CallState) -> str:
    """
    Route after processing the client's answer.
    - objection detected → objection handler
    - all questions answered → closing
    - more questions → ask next question
    """
    if state.get("objection_detected", False):
        return "objection_handler"

    current_idx = state.get("current_question_index", 0)
    total = state.get("total_questions", 0)

    if current_idx >= total:
        return "closing"
    else:
        return "question"


def route_after_objection(state: CallState) -> str:
    """
    Route after handling an objection.
    - terminal objection (not interested) → closing
    - handled successfully → back to questioning
    """
    call_phase = state.get("call_phase", "")

    if call_phase == "closing":
        return "closing"
    else:
        return "question"


def route_after_closing(state: CallState) -> str:
    """After closing, always go to post-call processing."""
    return "post_call"


def route_after_voicemail(state: CallState) -> str:
    """After voicemail, go to post-call."""
    return "post_call"


def should_continue_questioning(state: CallState) -> str:
    """
    Determine if we should continue asking questions or stop.
    Used as a conditional edge in the question loop.
    """
    current_idx = state.get("current_question_index", 0)
    total = state.get("total_questions", 0)
    max_turns = 30  # Safety limit

    if state.get("current_turn", 0) >= max_turns:
        return "closing"

    if current_idx >= total:
        return "closing"

    return "continue"
