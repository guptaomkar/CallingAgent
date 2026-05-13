# app/prompts/__init__.py
from app.prompts.system_persona import build_system_prompt
from app.prompts.call_opening import build_opening_prompt
from app.prompts.question_flow import build_question_flow_prompt
from app.prompts.objection_handling import build_objection_prompt
from app.prompts.post_call_extraction import build_extraction_prompt
from app.prompts.report_schema import REPORT_SCHEMA, OUTCOME_COLORS

__all__ = [
    "build_system_prompt",
    "build_opening_prompt",
    "build_question_flow_prompt",
    "build_objection_prompt",
    "build_extraction_prompt",
    "REPORT_SCHEMA",
    "OUTCOME_COLORS",
]
