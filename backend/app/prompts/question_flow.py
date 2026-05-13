# ============================================================
# Prompt 3 — Question Execution Flow
# File: app/prompts/question_flow.py
#
# Governs how the agent asks each question during the call.
# Questions are injected dynamically from the campaign config.
# ============================================================

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.campaign import Campaign


QUESTION_FLOW_TEMPLATE = """QUESTION FLOW EXECUTION
========================

You will ask the client the following questions, strictly one at a time,
in the order listed below.

RULES FOR ASKING QUESTIONS
---------------------------
1. Ask ONE question at a time. Never combine two questions in one turn.
2. After each answer, acknowledge it naturally before continuing.
   Use phrases like:
   - "Got it, thanks for sharing that!"
   - "That's really helpful, I appreciate that."
   - "Perfect, noted!"
   - "That makes complete sense."
3. If the client gives an unclear or incomplete answer, politely clarify:
   "Just to make sure I've captured that correctly — do you mean
   [Option A] or more like [Option B]?"
4. If the client goes off-topic, gently redirect:
   "That's really helpful context! Just to make sure I note everything
   correctly — [rephrase or repeat the question]."
5. Record the client's answer verbatim — do not paraphrase.
6. If a client skips a question or says "I don't know", log it as
   "not answered" and continue to the next question.
7. Never repeat a question the client has already answered.

QUESTIONS TO ASK
----------------
{questions_list}

AFTER ALL QUESTIONS ARE ANSWERED
---------------------------------
Move to the closing script:

"Wonderful! Thank you so much for your time today, [CLIENT_NAME].
I've captured everything and our team will {next_step}.

Is there anything else you'd like to know about {service_name}
before we wrap up?"

[Address any final questions, then close]

"It was a pleasure speaking with you. Have a fantastic day! Goodbye!"
"""


def build_question_flow_prompt(campaign: Campaign) -> str:
    """
    Build the question flow prompt with campaign-specific questions.

    Args:
        campaign: Campaign with questions list in JSON

    Returns:
        Rendered question flow prompt
    """
    questions = campaign.questions or []

    # Format questions list
    questions_lines = []
    for i, q in enumerate(questions, 1):
        q_text = q.get("text", "") if isinstance(q, dict) else str(q)
        q_id = q.get("id", f"q{i}") if isinstance(q, dict) else f"q{i}"
        questions_lines.append(f"Q{i} ({q_id}): \"{q_text}\"")

    questions_list = "\n".join(questions_lines) if questions_lines else "No questions configured."

    next_step = "be in touch within 24 hours to follow up"

    return QUESTION_FLOW_TEMPLATE.format(
        questions_list=questions_list,
        next_step=next_step,
        service_name=campaign.service_name,
    )
