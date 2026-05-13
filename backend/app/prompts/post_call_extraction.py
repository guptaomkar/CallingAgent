# ============================================================
# Prompt 5 — Post-Call Response Extraction
# File: app/prompts/post_call_extraction.py
#
# Sent to the LLM after every call with the full transcript.
# Returns structured JSON for Excel population.
# ============================================================

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.campaign import Campaign


POST_CALL_EXTRACTION_TEMPLATE = """POST-CALL RESPONSE EXTRACTION
==============================

You are a data extraction specialist. You will be given the full
transcript of a sales call. Your job is to extract all structured
data from the conversation and return it as a valid JSON object.

TRANSCRIPT:
\"\"\"
{transcript}
\"\"\"

CAMPAIGN CONTEXT:
- Agent Name: {agent_name}
- Company: {company_name}
- Service: {service_name}
- Campaign ID: {campaign_id}

QUESTIONS THAT WERE ASKED:
{questions_reference}

EXTRACTION INSTRUCTIONS
-----------------------
- Extract answers to each question based on what the client said.
- If a question was not asked or not answered, set the value to null.
- Do not infer or guess answers — use only what the client explicitly said.
- For sentiment, analyse the overall tone of the client's responses.
- For call_outcome, choose the best-fit category from the allowed values.

FIELDS TO EXTRACT
-----------------
{{
  "client_name":              string,
  "phone_number":             string (E.164 format),
  "call_date":                string (ISO 8601: YYYY-MM-DD),
  "call_time":                string (HH:MM in 24hr format),
  "call_duration_seconds":    integer,
  "agent_name":               string,
  "campaign_id":              string,
  "call_outcome":             one of [
                                "interested",
                                "not_interested",
                                "callback_requested",
                                "voicemail",
                                "no_answer",
                                "incomplete"
                              ],
  {question_fields}
  "preferred_callback_time":  string or null,
  "email_requested":          boolean,
  "demo_requested":           boolean,
  "sentiment":                one of ["positive", "neutral", "negative"],
  "objections_raised":        array of strings (list each objection the client raised),
  "additional_notes":         string (any notable comments or context from the client)
}}

OUTPUT RULES
------------
- Return ONLY valid JSON. No explanation. No markdown. No code blocks.
- Every key must be present. Use null for missing values, not empty string.
- Ensure the JSON is parseable without modification.
"""


def build_extraction_prompt(
    transcript: str,
    campaign: Campaign,
    client_name: str = "",
    phone_number: str = "",
    call_duration: int = 0,
) -> str:
    """
    Build the post-call extraction prompt with the full transcript.

    Args:
        transcript: Full call transcript text
        campaign: Campaign configuration
        client_name: Client's name
        phone_number: Client's phone number
        call_duration: Call duration in seconds

    Returns:
        Rendered extraction prompt
    """
    questions = campaign.questions or []

    # Build questions reference
    questions_lines = []
    for i, q in enumerate(questions, 1):
        q_text = q.get("text", "") if isinstance(q, dict) else str(q)
        questions_lines.append(f"Q{i}: \"{q_text}\"")
    questions_reference = "\n".join(questions_lines) if questions_lines else "No questions configured."

    # Build question answer fields for JSON schema
    question_fields_lines = []
    for i in range(1, len(questions) + 1):
        question_fields_lines.append(f'  "question_{i}_answer":        string or null,')
    question_fields = "\n".join(question_fields_lines) if question_fields_lines else '  "question_1_answer": string or null,'

    return POST_CALL_EXTRACTION_TEMPLATE.format(
        transcript=transcript,
        agent_name=campaign.agent_name,
        company_name=campaign.company_name,
        service_name=campaign.service_name,
        campaign_id=campaign.campaign_id,
        questions_reference=questions_reference,
        question_fields=question_fields,
    )
