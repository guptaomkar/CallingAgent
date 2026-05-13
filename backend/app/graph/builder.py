# ============================================================
# LangGraph Call Flow Builder
# File: app/graph/builder.py
#
# Compiles the full LangGraph state machine for a call session.
# ============================================================

import logging

from langgraph.graph import END, StateGraph

from app.graph.state import CallState
from app.graph.nodes import (
    greeting_node,
    consent_check_node,
    question_node,
    answer_processing_node,
    objection_handler_node,
    closing_node,
    voicemail_node,
    post_call_node,
)
from app.graph.edges import (
    route_after_consent,
    route_after_answer,
    route_after_objection,
)

logger = logging.getLogger(__name__)


def build_call_graph() -> StateGraph:
    """
    Build and compile the LangGraph state machine for call flow.

    The graph implements this flow:

        START
          │
          ▼
       greeting ──────────► consent_check
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
               voicemail    question     closing
                    │           │           │
                    │     ┌─────┴─────┐     │
                    │     ▼           ▼     │
                    │  answer_proc  (loop)  │
                    │     │                 │
                    │     ├──► objection    │
                    │     │     handler     │
                    │     │        │        │
                    │     │        ▼        │
                    │     └──► question     │
                    │                       │
                    ▼                       ▼
                post_call ◄────────── post_call
                    │
                    ▼
                   END

    Returns:
        Compiled StateGraph ready for invocation
    """
    # Create the graph
    graph = StateGraph(CallState)

    # Add all nodes
    graph.add_node("greeting", greeting_node)
    graph.add_node("consent_check", consent_check_node)
    graph.add_node("question", question_node)
    graph.add_node("answer_processing", answer_processing_node)
    graph.add_node("objection_handler", objection_handler_node)
    graph.add_node("closing", closing_node)
    graph.add_node("voicemail", voicemail_node)
    graph.add_node("post_call", post_call_node)

    # Set entry point
    graph.set_entry_point("greeting")

    # Define edges
    # greeting → consent_check (always)
    graph.add_edge("greeting", "consent_check")

    # consent_check → {voicemail, question, closing} (conditional)
    graph.add_conditional_edges(
        "consent_check",
        route_after_consent,
        {
            "voicemail": "voicemail",
            "question": "question",
            "closing": "closing",
        },
    )

    # question → answer_processing (always; agent asks, then waits for answer)
    graph.add_edge("question", "answer_processing")

    # answer_processing → {objection_handler, question, closing} (conditional)
    graph.add_conditional_edges(
        "answer_processing",
        route_after_answer,
        {
            "objection_handler": "objection_handler",
            "question": "question",
            "closing": "closing",
        },
    )

    # objection_handler → {question, closing} (conditional)
    graph.add_conditional_edges(
        "objection_handler",
        route_after_objection,
        {
            "question": "question",
            "closing": "closing",
        },
    )

    # closing → post_call (always)
    graph.add_edge("closing", "post_call")

    # voicemail → post_call (always)
    graph.add_edge("voicemail", "post_call")

    # post_call → END (always)
    graph.add_edge("post_call", END)

    # Compile the graph
    compiled = graph.compile()
    logger.info("✅ LangGraph call flow compiled successfully")

    return compiled


def create_initial_state(
    session_id: str,
    campaign: dict,
    contact: dict,
) -> CallState:
    """
    Create the initial state for a new call session.

    Args:
        session_id: Unique call session identifier
        campaign: Campaign configuration dict
        contact: Contact information dict

    Returns:
        Initial CallState for the graph
    """
    questions = campaign.get("questions", [])

    return CallState(
        session_id=session_id,
        contact=contact,
        campaign=campaign,
        messages=[],
        current_turn=0,
        current_question_index=0,
        total_questions=len(questions),
        questions_answered={},
        call_phase="greeting",
        consent_given=None,
        objection_detected=False,
        last_objection=None,
        call_outcome=None,
        sentiment=None,
        callback_requested=False,
        preferred_callback_time=None,
        email_requested=False,
        demo_requested=False,
        objections_raised=[],
        call_status="initiated",
        error=None,
        additional_notes="",
    )
