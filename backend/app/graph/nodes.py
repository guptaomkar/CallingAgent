# ============================================================
# LangGraph Nodes — Call Flow Functions
# File: app/graph/nodes.py
#
# Each node is a function that receives CallState,
# performs an action, and returns updated state fields.
# ============================================================

import json
import logging
from datetime import datetime

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from openai import OpenAI

from app.config import get_settings
from app.graph.state import CallState

logger = logging.getLogger(__name__)
settings = get_settings()

# Shared OpenAI client
_openai_client = None


def _get_openai_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=settings.openai_api_key)
    return _openai_client


def _call_llm(messages: list[dict], temperature: float = 0.7) -> str:
    """Send messages to GPT-4.1 and get a response."""
    client = _get_openai_client()
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        temperature=temperature,
        max_tokens=500,
    )
    return response.choices[0].message.content.strip()


# ===================================================================
# NODE: Greeting
# ===================================================================
def greeting_node(state: CallState) -> dict:
    """
    First node — the agent introduces itself and asks for consent.
    Uses the opening script from Prompt 2.
    """
    campaign = state["campaign"]
    contact = state["contact"]

    from app.prompts.call_opening import build_opening_prompt
    opening = build_opening_prompt_from_dict(campaign, contact)

    logger.info(f"[{state['session_id']}] Greeting: {contact.get('client_name', 'Unknown')}")

    return {
        "messages": [AIMessage(content=opening)],
        "call_phase": "consent",
        "current_turn": state.get("current_turn", 0) + 1,
        "call_status": "in_progress",
    }


# ===================================================================
# NODE: Consent Check
# ===================================================================
def consent_check_node(state: CallState) -> dict:
    """
    Analyze the client's response to determine:
    - consent_given (proceed to questions)
    - busy (schedule callback)
    - not interested (end call)
    """
    messages = state["messages"]
    if not messages:
        return {"consent_given": None, "call_phase": "closing"}

    last_message = messages[-1].content if messages else ""

    # Use LLM to classify consent
    classification_prompt = [
        {"role": "system", "content": (
            "You are analyzing a phone call response. The agent just introduced "
            "themselves and asked if the client has time for a few questions. "
            "Classify the client's response as one of: "
            "'consent' (they agreed), 'busy' (they said they're busy), "
            "'not_interested' (they declined), 'voicemail' (no real response/machine). "
            "Return ONLY the classification word, nothing else."
        )},
        {"role": "user", "content": f"Client's response: \"{last_message}\""},
    ]

    classification = _call_llm(classification_prompt, temperature=0.1).lower().strip()
    logger.info(f"[{state['session_id']}] Consent classification: {classification}")

    if classification == "consent":
        return {
            "consent_given": True,
            "call_phase": "questioning",
            "current_turn": state.get("current_turn", 0) + 1,
        }
    elif classification == "busy":
        return {
            "consent_given": False,
            "call_phase": "closing",
            "callback_requested": True,
            "call_outcome": "callback_requested",
            "current_turn": state.get("current_turn", 0) + 1,
        }
    elif classification == "voicemail":
        return {
            "consent_given": False,
            "call_phase": "voicemail",
            "call_outcome": "voicemail",
        }
    else:  # not_interested or unknown
        return {
            "consent_given": False,
            "call_phase": "closing",
            "call_outcome": "not_interested",
            "current_turn": state.get("current_turn", 0) + 1,
        }


# ===================================================================
# NODE: Question Asking
# ===================================================================
def question_node(state: CallState) -> dict:
    """
    Ask the next question in the sequence.
    Acknowledges the previous answer first, then asks the next question.
    """
    campaign = state["campaign"]
    questions = campaign.get("questions", [])
    current_idx = state.get("current_question_index", 0)
    questions_answered = state.get("questions_answered", {})

    # If all questions answered, move to closing
    if current_idx >= len(questions):
        logger.info(f"[{state['session_id']}] All {len(questions)} questions answered")
        return {
            "call_phase": "closing",
            "call_outcome": "interested",  # Completed all questions = interested
        }

    # Get the current question
    q = questions[current_idx]
    q_text = q.get("text", "") if isinstance(q, dict) else str(q)
    q_id = q.get("id", f"q{current_idx + 1}") if isinstance(q, dict) else f"q{current_idx + 1}"

    # Build the message to send
    # If this isn't the first question, acknowledge the previous answer
    messages_for_llm = _build_llm_messages(state)
    messages_for_llm.append({
        "role": "user",
        "content": (
            f"You've just received the client's response. "
            f"First, briefly and naturally acknowledge their answer. "
            f"Then smoothly transition to asking the next question: \"{q_text}\". "
            f"Keep it conversational and natural. Do NOT combine multiple questions."
        ),
    })

    agent_response = _call_llm(messages_for_llm)

    logger.info(f"[{state['session_id']}] Asked Q{current_idx + 1}: {q_text[:50]}...")

    return {
        "messages": [AIMessage(content=agent_response)],
        "current_turn": state.get("current_turn", 0) + 1,
    }


# ===================================================================
# NODE: Answer Processing
# ===================================================================
def answer_processing_node(state: CallState) -> dict:
    """
    Process the client's answer to the current question.
    Detects objections and stores the answer.
    """
    messages = state["messages"]
    campaign = state["campaign"]
    questions = campaign.get("questions", [])
    current_idx = state.get("current_question_index", 0)
    questions_answered = dict(state.get("questions_answered", {}))

    if not messages:
        return {}

    last_message = messages[-1].content if messages else ""

    # Get current question
    if current_idx < len(questions):
        q = questions[current_idx]
        q_id = q.get("id", f"q{current_idx + 1}") if isinstance(q, dict) else f"q{current_idx + 1}"

        # Store the answer
        questions_answered[q_id] = last_message

    # Check for objection in the response
    objection_check = [
        {"role": "system", "content": (
            "Analyze this phone call response. Does the client raise an objection "
            "or express resistance? Objections include: not interested, too busy, "
            "too expensive, using competitor, need to think, never heard of company, "
            "just send email. "
            "Respond with JSON: {\"is_objection\": true/false, \"objection_type\": \"...\" or null}"
        )},
        {"role": "user", "content": f"Client said: \"{last_message}\""},
    ]

    objection_result = _call_llm(objection_check, temperature=0.1)

    try:
        objection_data = json.loads(objection_result)
        is_objection = objection_data.get("is_objection", False)
        objection_type = objection_data.get("objection_type")
    except (json.JSONDecodeError, KeyError):
        is_objection = False
        objection_type = None

    result = {
        "questions_answered": questions_answered,
        "current_question_index": current_idx + 1,
        "current_turn": state.get("current_turn", 0) + 1,
    }

    if is_objection:
        objections = list(state.get("objections_raised", []))
        objections.append(objection_type or last_message)
        result.update({
            "objection_detected": True,
            "last_objection": objection_type or last_message,
            "objections_raised": objections,
            "call_phase": "objection",
        })
    else:
        result["objection_detected"] = False

    return result


# ===================================================================
# NODE: Objection Handler
# ===================================================================
def objection_handler_node(state: CallState) -> dict:
    """
    Handle an objection using the objection handling guide (Prompt 4).
    Responds warmly and attempts to continue or close gracefully.
    """
    campaign = state["campaign"]
    last_objection = state.get("last_objection", "")

    from app.prompts.objection_handling import build_objection_prompt
    objection_guide = build_objection_prompt_from_dict(campaign)

    messages_for_llm = _build_llm_messages(state)
    messages_for_llm.append({
        "role": "system",
        "content": (
            f"The client just raised an objection: \"{last_objection}\"\n\n"
            f"Use this objection handling guide to respond:\n{objection_guide}\n\n"
            f"Respond naturally and warmly. If the objection is terminal "
            f"(like 'not interested' or 'remove me'), accept it graciously. "
            f"Otherwise, address it and try to continue the conversation."
        ),
    })

    agent_response = _call_llm(messages_for_llm)

    logger.info(f"[{state['session_id']}] Handled objection: {last_objection}")

    # Determine if this is a terminal objection
    terminal_objections = ["not interested", "not_interested", "remove me", "stop calling"]
    is_terminal = any(t in (last_objection or "").lower() for t in terminal_objections)

    result = {
        "messages": [AIMessage(content=agent_response)],
        "objection_detected": False,
        "current_turn": state.get("current_turn", 0) + 1,
    }

    if is_terminal:
        result.update({
            "call_phase": "closing",
            "call_outcome": "not_interested",
        })
    else:
        result["call_phase"] = "questioning"

    return result


# ===================================================================
# NODE: Closing
# ===================================================================
def closing_node(state: CallState) -> dict:
    """
    Close the call gracefully. Thank the client and confirm next steps.
    """
    campaign = state["campaign"]
    contact = state["contact"]
    client_name = contact.get("client_name", "")
    call_outcome = state.get("call_outcome", "incomplete")

    messages_for_llm = _build_llm_messages(state)

    if call_outcome == "interested":
        closing_instruction = (
            f"All questions have been answered. Thank {client_name} warmly for their time. "
            f"Confirm next steps: the team will follow up within 24 hours. "
            f"Ask if there's anything else they'd like to know about {campaign.get('service_name', 'our service')}. "
            f"End with a warm goodbye."
        )
    elif call_outcome == "callback_requested":
        closing_instruction = (
            f"The client is busy. Politely ask when would be a better time to call back. "
            f"Thank them and end warmly."
        )
    elif call_outcome == "not_interested":
        closing_instruction = (
            f"The client is not interested. Thank them graciously for their time. "
            f"Wish them well and end the call warmly. Do NOT try to convince them."
        )
    else:
        closing_instruction = (
            f"End the call naturally. Thank {client_name} for their time and wish them well."
        )

    messages_for_llm.append({"role": "user", "content": closing_instruction})

    agent_response = _call_llm(messages_for_llm)

    logger.info(f"[{state['session_id']}] Closing call. Outcome: {call_outcome}")

    return {
        "messages": [AIMessage(content=agent_response)],
        "call_phase": "post_call",
        "call_status": "completed",
        "call_outcome": call_outcome or "incomplete",
        "current_turn": state.get("current_turn", 0) + 1,
    }


# ===================================================================
# NODE: Voicemail
# ===================================================================
def voicemail_node(state: CallState) -> dict:
    """Leave a voicemail message."""
    campaign = state["campaign"]

    from app.prompts.call_opening import build_voicemail_message
    voicemail = VOICEMAIL_TEMPLATE.format(
        agent_name=campaign.get("agent_name", ""),
        company_name=campaign.get("company_name", ""),
    )

    logger.info(f"[{state['session_id']}] Leaving voicemail")

    return {
        "messages": [AIMessage(content=voicemail)],
        "call_phase": "post_call",
        "call_status": "completed",
        "call_outcome": "voicemail",
    }


# ===================================================================
# NODE: Post-Call Processing
# ===================================================================
def post_call_node(state: CallState) -> dict:
    """
    Final node — extract structured data from the conversation.
    This runs AFTER the call has ended.
    """
    campaign = state["campaign"]
    contact = state["contact"]
    messages = state.get("messages", [])

    # Build transcript from message history
    transcript_lines = []
    for msg in messages:
        role = "Agent" if isinstance(msg, AIMessage) else "Client"
        transcript_lines.append(f"{role}: {msg.content}")
    transcript = "\n".join(transcript_lines)

    # Use Prompt 5 for extraction
    from app.prompts.post_call_extraction import build_extraction_prompt

    # Create a simple campaign object-like dict for the prompt builder
    extraction_prompt = build_extraction_prompt_from_dict(
        transcript=transcript,
        campaign=campaign,
        client_name=contact.get("client_name", ""),
        phone_number=contact.get("phone_number", ""),
    )

    extraction_messages = [
        {"role": "system", "content": "You are a data extraction specialist. Return ONLY valid JSON."},
        {"role": "user", "content": extraction_prompt},
    ]

    extracted_json_str = _call_llm(extraction_messages, temperature=0.1)

    try:
        # Clean up potential markdown code block wrapping
        cleaned = extracted_json_str.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
            cleaned = cleaned.rsplit("```", 1)[0]
        extracted_data = json.loads(cleaned)
    except json.JSONDecodeError:
        logger.error(f"[{state['session_id']}] Failed to parse extraction JSON")
        extracted_data = {}

    logger.info(f"[{state['session_id']}] Post-call extraction complete")

    # Determine final sentiment from extracted data or conversation
    sentiment = extracted_data.get("sentiment", state.get("sentiment", "neutral"))

    return {
        "call_phase": "completed",
        "sentiment": sentiment,
        "additional_notes": extracted_data.get("additional_notes", ""),
        "email_requested": extracted_data.get("email_requested", False),
        "demo_requested": extracted_data.get("demo_requested", False),
    }


# ===================================================================
# HELPER FUNCTIONS
# ===================================================================

def _build_llm_messages(state: CallState, max_turns: int = 10) -> list[dict]:
    """
    Build LLM message list from state, including system prompt.
    Keeps only the last `max_turns` messages to manage context window.
    """
    campaign = state["campaign"]
    contact = state["contact"]

    from app.prompts.system_persona import build_system_prompt

    # Build system prompt from dict data
    system_prompt = build_system_prompt_from_dict(campaign, contact)

    llm_messages = [{"role": "system", "content": system_prompt}]

    # Add conversation history (last N turns)
    messages = state.get("messages", [])
    recent_messages = messages[-max_turns:] if len(messages) > max_turns else messages

    for msg in recent_messages:
        if isinstance(msg, AIMessage):
            llm_messages.append({"role": "assistant", "content": msg.content})
        elif isinstance(msg, HumanMessage):
            llm_messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, SystemMessage):
            llm_messages.append({"role": "system", "content": msg.content})

    return llm_messages


# --- Dict-based prompt builders (for use within graph nodes) ---
# These work with raw dicts instead of ORM models

VOICEMAIL_TEMPLATE = (
    "Hi, this is {agent_name} from {company_name}. "
    "I was calling to share something that may be valuable for you. "
    "Please call us back or we'll try you again soon. Have a wonderful day!"
)


def build_system_prompt_from_dict(campaign: dict, contact: dict) -> str:
    """Build system prompt from dict data (used inside graph nodes)."""
    from app.prompts.system_persona import SYSTEM_PERSONA_TEMPLATE

    max_duration = campaign.get("max_call_duration_seconds", 300)
    client_notes = ""
    if contact.get("notes"):
        client_notes = f"Pre-call notes: {contact['notes']}"

    return SYSTEM_PERSONA_TEMPLATE.format(
        agent_name=campaign.get("agent_name", "Agent"),
        company_name=campaign.get("company_name", "Our Company"),
        campaign_objective=campaign.get("campaign_objective", ""),
        service_name=campaign.get("service_name", "Our Service"),
        service_description=campaign.get("service_description", ""),
        language=campaign.get("language", "English"),
        max_duration=max_duration,
        max_minutes=max_duration // 60,
        client_name=contact.get("client_name", "the client"),
        client_notes=client_notes,
    )


def build_opening_prompt_from_dict(campaign: dict, contact: dict) -> str:
    """Build opening prompt from dict data."""
    from app.prompts.call_opening import CALL_OPENING_TEMPLATE

    return CALL_OPENING_TEMPLATE.format(
        client_name=contact.get("client_name", "there"),
        agent_name=campaign.get("agent_name", "Agent"),
        company_name=campaign.get("company_name", "Our Company"),
        brief_reason=(
            f"we recently launched {campaign.get('service_name', 'a new service')} "
            f"and I believe it could be really valuable for you"
        ),
    )


def build_objection_prompt_from_dict(campaign: dict) -> str:
    """Build objection prompt from dict data."""
    from app.prompts.objection_handling import OBJECTION_HANDLING_TEMPLATE

    return OBJECTION_HANDLING_TEMPLATE.format(
        company_name=campaign.get("company_name", "Our Company"),
        service_name=campaign.get("service_name", "Our Service"),
        key_differentiator=f"unique approach to {campaign.get('service_name', 'our service')}",
    )


def build_extraction_prompt_from_dict(
    transcript: str,
    campaign: dict,
    client_name: str = "",
    phone_number: str = "",
) -> str:
    """Build extraction prompt from dict data."""
    from app.prompts.post_call_extraction import POST_CALL_EXTRACTION_TEMPLATE

    questions = campaign.get("questions", [])
    questions_lines = []
    for i, q in enumerate(questions, 1):
        q_text = q.get("text", f"Question {i}") if isinstance(q, dict) else str(q)
        questions_lines.append(f"Q{i}: \"{q_text}\"")
    questions_reference = "\n".join(questions_lines)

    question_fields_lines = []
    for i in range(1, len(questions) + 1):
        question_fields_lines.append(f'  "question_{i}_answer":        string or null,')
    question_fields = "\n".join(question_fields_lines) or '  "question_1_answer": string or null,'

    return POST_CALL_EXTRACTION_TEMPLATE.format(
        transcript=transcript,
        agent_name=campaign.get("agent_name", ""),
        company_name=campaign.get("company_name", ""),
        service_name=campaign.get("service_name", ""),
        campaign_id=campaign.get("campaign_id", ""),
        questions_reference=questions_reference,
        question_fields=question_fields,
    )
