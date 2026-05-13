# ============================================================
# Prompt 6 — Excel Report Schema Configuration
# File: app/prompts/report_schema.py
#
# Python configuration used by the Excel report writer to map
# extracted JSON fields to Excel columns.
# ============================================================

# Column-to-field mapping for the Excel report
REPORT_SCHEMA = {
    "A": {"header": "Client Name",             "json_key": "client_name"},
    "B": {"header": "Phone Number",            "json_key": "phone_number"},
    "C": {"header": "Call Date",               "json_key": "call_date"},
    "D": {"header": "Call Time",               "json_key": "call_time"},
    "E": {"header": "Duration (sec)",          "json_key": "call_duration_seconds"},
    "F": {"header": "Agent Name",              "json_key": "agent_name"},
    "G": {"header": "Campaign ID",             "json_key": "campaign_id"},
    "H": {"header": "Call Outcome",            "json_key": "call_outcome"},
    # Question columns are dynamic — added based on campaign config
    # Columns I–M are reserved for Q1–Q5 but can extend further
    "N": {"header": "Callback Time",           "json_key": "preferred_callback_time"},
    "O": {"header": "Email Requested",         "json_key": "email_requested"},
    "P": {"header": "Demo Requested",          "json_key": "demo_requested"},
    "Q": {"header": "Sentiment",               "json_key": "sentiment"},
    "R": {"header": "Objections Raised",       "json_key": "objections_raised"},
    "S": {"header": "Additional Notes",        "json_key": "additional_notes"},
}

# Row color coding by call outcome
OUTCOME_COLORS = {
    "interested":          "C6EFCE",   # Green
    "callback_requested":  "FFEB9C",   # Yellow
    "not_interested":      "FFC7CE",   # Red
    "voicemail":           "D9D9D9",   # Gray
    "no_answer":           "D9D9D9",   # Gray
    "incomplete":          "FCE4D6",   # Orange
}

# Header row styling
HEADER_STYLE = {
    "fill_color": "1F4E79",       # Dark navy
    "font_color": "FFFFFF",       # White
    "font_bold": True,
    "row_height": 24,
}

# Data row styling
DATA_STYLE = {
    "row_height": 18,
    "font_size": 11,
}

# Tab configuration
REPORT_TABS = {
    "all_calls": {
        "name": "All Calls",
        "description": "Every call regardless of outcome",
        "filter": None,  # No filter — includes all
    },
    "interested": {
        "name": "Interested",
        "description": "Filtered view — interested clients only",
        "filter": {"call_outcome": "interested"},
    },
    "callbacks": {
        "name": "Callbacks",
        "description": "Clients who requested a callback",
        "filter": {"call_outcome": "callback_requested"},
    },
    "no_contact": {
        "name": "No Contact",
        "description": "Voicemail + no answer entries",
        "filter": {"call_outcome": ["voicemail", "no_answer"]},
    },
    "summary": {
        "name": "Summary",
        "description": "Campaign-level stats",
        "filter": "summary",  # Special handling
    },
}


def build_dynamic_schema(questions: list[dict]) -> dict:
    """
    Build the full report schema including dynamic question columns.

    Args:
        questions: List of question dicts from campaign config

    Returns:
        Complete column-to-field mapping dict
    """
    schema = {}

    # Static columns A–H
    static_cols = ["A", "B", "C", "D", "E", "F", "G", "H"]
    for col in static_cols:
        schema[col] = REPORT_SCHEMA[col].copy()

    # Dynamic question columns (I onward)
    q_start_col = ord("I")
    for i, q in enumerate(questions):
        col_letter = chr(q_start_col + i)
        q_text = q.get("text", f"Question {i+1}") if isinstance(q, dict) else str(q)
        q_id = q.get("id", f"q{i+1}") if isinstance(q, dict) else f"q{i+1}"

        # Truncate question text for header if too long
        header_text = f"Q{i+1} — {q_text}"
        if len(header_text) > 50:
            header_text = header_text[:47] + "..."

        schema[col_letter] = {
            "header": header_text,
            "json_key": f"question_{i+1}_answer",
        }

    # Remaining static columns after questions
    remaining_start = chr(q_start_col + len(questions))
    remaining_keys = ["N", "O", "P", "Q", "R", "S"]
    for offset, orig_key in enumerate(remaining_keys):
        new_col = chr(ord(remaining_start) + offset)
        schema[new_col] = REPORT_SCHEMA[orig_key].copy()

    return schema
