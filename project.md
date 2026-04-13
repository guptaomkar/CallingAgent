# AI Calling Agent — Full Engineering Blueprint

> **Project:** Autonomous AI Voice Calling Agent for Sales & Service Promotion  
> **Version:** 1.0  
> **Prepared by:** AI Engineering Team  
> **Document Type:** Architecture + Prompt Engineering Reference

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Component Breakdown](#4-component-breakdown)
5. [Data Flow](#5-data-flow)
6. [Prompt Engineering — Full Prompt Library](#6-prompt-engineering--full-prompt-library)
   - [Prompt 1 — System Persona Prompt](#prompt-1--system-persona-prompt)
   - [Prompt 2 — Call Opening Script](#prompt-2--call-opening-script)
   - [Prompt 3 — Question Execution Flow](#prompt-3--question-execution-flow)
   - [Prompt 4 — Objection Handling](#prompt-4--objection-handling)
   - [Prompt 5 — Post-Call Response Extraction](#prompt-5--post-call-response-extraction)
   - [Prompt 6 — Excel Report Schema Config](#prompt-6--excel-report-schema-config)
7. [Input File Specifications](#7-input-file-specifications)
8. [Output Excel Report Structure](#8-output-excel-report-structure)
9. [Implementation Roadmap](#9-implementation-roadmap)
10. [Security & Compliance Considerations](#10-security--compliance-considerations)
11. [Scalability Notes](#11-scalability-notes)

---

## 1. Project Overview

### What We Are Building

An AI-powered autonomous voice calling agent that:

- Reads a client contact list from an Excel/CSV input file
- Dials each client using a cloud telephony provider
- Speaks naturally and human-like, promoting services and gathering structured responses
- Asks a predefined set of questions during each call
- Handles objections intelligently using dynamic conversation logic
- Transcribes and extracts answers using NLP post-processing
- Automatically fills an Excel report with all call outcomes and responses

### Core Goals

| Goal | Description |
|------|-------------|
| Human-like voice | Agent must sound natural, warm, and conversational — not robotic |
| Campaign flexibility | Questions, services, and tone must be configurable per campaign |
| Structured output | Every call produces a clean, filled Excel report row |
| Scalable calling | Support batch dialing of 100s to 1000s of contacts |
| Objection handling | Agent dynamically responds to pushback without breaking the script |

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        INPUT LAYER                              │
│                                                                 │
│  ┌──────────────┐  ┌──────────────────┐  ┌─────────────────┐  │
│  │  Client List │  │  Question Script │  │ Campaign Brief  │  │
│  │ (Excel/CSV)  │  │   (JSON/YAML)    │  │ (Service config)│  │
│  └──────┬───────┘  └────────┬─────────┘  └────────┬────────┘  │
└─────────┼────────────────────┼─────────────────────┼───────────┘
          │                    │                     │
          └────────────────────┼─────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR LAYER                          │
│                                                                 │
│   ┌──────────────────────────────────────────────────────┐     │
│   │            Orchestrator Agent (LangGraph)            │     │
│   │   Prompt engine · Session manager · Retry logic      │     │
│   │   Call queue · State machine · Logging               │     │
│   └──────────────────────────┬───────────────────────────┘     │
└──────────────────────────────┼──────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      VOICE AI LAYER                             │
│                                                                 │
│  ┌────────────────────────┐    ┌───────────────────────────┐   │
│  │     LLM Brain          │◄──►│    TTS / STT Engine       │   │
│  │  (Claude / GPT-4o)     │    │  ElevenLabs + Deepgram    │   │
│  │  Conversation logic    │    │  Real-time speech I/O     │   │
│  │  Objection handling    │    │  Human voice cloning      │   │
│  └────────────────────────┘    └───────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     TELEPHONY LAYER                             │
│                                                                 │
│   ┌──────────────────────────────────────────────────────┐     │
│   │     Twilio Voice / Vapi.ai  ·  PSTN / SIP            │     │
│   │     Outbound dialer · Call session management        │     │
│   │     DTMF detection · Call recording                  │     │
│   └──────────────────────────┬───────────────────────────┘     │
└──────────────────────────────┼──────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OUTPUT LAYER                               │
│                                                                 │
│  ┌────────────────────────┐    ┌───────────────────────────┐   │
│  │   Response Extractor   │───►│    Excel Report Writer    │   │
│  │   NLP + Answer mapper  │    │    openpyxl + auto-fill   │   │
│  │   Sentiment analysis   │    │    Color-coded outcomes   │   │
│  └────────────────────────┘    └───────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **LLM Brain** | Claude Sonnet 3.5 / GPT-4o | Conversation logic, objection handling, NLP extraction |
| **Text-to-Speech** | ElevenLabs (Turbo v2.5) | Ultra-realistic human voice synthesis |
| **Speech-to-Text** | Deepgram Nova-2 | Real-time transcription with low latency |
| **Telephony** | Twilio Voice API / Vapi.ai | Outbound calling, call sessions, recording |
| **Orchestration** | LangGraph (Python) | Multi-turn state machine for call flow |
| **Backend** | FastAPI (Python 3.11+) | REST API, webhook handler, job runner |
| **Task Queue** | Redis + Celery | Batch call scheduling and retry management |
| **Database** | PostgreSQL | Call logs, session history, client data |
| **Report Output** | openpyxl | Excel file generation and formatting |
| **Deployment** | Docker + AWS / GCP | Scalable containerized deployment |

---

## 4. Component Breakdown

### 4.1 Input Processor

Responsible for reading and validating the client contact list and campaign configuration before any calls are made.

**Inputs accepted:**
- Excel `.xlsx` or `.csv` file with client contact data
- JSON or YAML campaign configuration (questions, service info, tone)
- Optional: CRM export or API-fetched contact list

**Validation checks:**
- Phone number format (E.164 standard)
- Required fields present (name, phone, campaign ID)
- Deduplication of contacts
- DND (Do Not Disturb) list exclusion

### 4.2 Orchestrator Agent

The central brain that manages every call session from start to finish.

**Responsibilities:**
- Assigns a unique session ID to each call
- Injects the correct system prompt, questions, and service context per campaign
- Manages call state: `initiated → ringing → connected → in_progress → completed / failed`
- Handles retry logic: no answer, voicemail, busy signal
- Tracks question progress during live calls
- Triggers post-call extraction and report writing

### 4.3 Voice AI Module

Handles the real-time spoken conversation.

**Sub-components:**

- **LLM Engine:** Receives transcribed text from STT, generates the agent's next response using the loaded prompts and conversation history
- **TTS Engine:** Converts LLM text output to natural speech audio using ElevenLabs. A cloned or tuned voice is used for maximum human resemblance
- **STT Engine:** Streams the client's spoken audio through Deepgram for real-time transcription with speaker diarization
- **Response delay simulator:** Adds 0.3–0.8 seconds of realistic pause before agent speaks to simulate human thinking time

### 4.4 Telephony Layer

Manages the actual phone calls.

**Key features:**
- Outbound PSTN calling via Twilio Programmable Voice or Vapi.ai
- Audio streaming over WebSocket for real-time TTS/STT integration
- Call recording (stored encrypted in S3)
- Voicemail detection (AMD — Answering Machine Detection)
- DTMF tone detection for IVR bypass

### 4.5 Post-Call Processor

Runs immediately after a call ends.

**Steps:**
1. Retrieve full call transcript from STT logs
2. Send transcript to LLM extraction prompt (Prompt 5)
3. Parse structured JSON response
4. Validate all required fields are present
5. Write row to Excel report via openpyxl
6. Update call status in PostgreSQL
7. Trigger callback scheduler if client requested a callback

---

## 5. Data Flow

```
[Client Excel File]
       │
       ▼
[Input Processor] ──validates──► [PostgreSQL: contacts table]
       │
       ▼
[Call Queue (Redis)] ──pops next contact──►
       │
       ▼
[Orchestrator: session_id created, prompts loaded]
       │
       ▼
[Twilio/Vapi: outbound call initiated]
       │
       ├── No Answer / Voicemail ──► [Schedule retry] ──► [Log outcome]
       │
       └── Connected
              │
              ▼
       [Deepgram STT: stream client audio]
              │
              ▼
       [LLM (Claude/GPT-4o): generate response]
              │
              ▼
       [ElevenLabs TTS: synthesize agent voice]
              │
              ▼
       [Twilio: play audio to client]
              │
       [Loop until all questions answered or call ends]
              │
              ▼
       [Full transcript stored]
              │
              ▼
       [LLM Extraction Prompt: parse answers → JSON]
              │
              ▼
       [openpyxl: write row to Excel report]
              │
              ▼
       [Report saved / emailed / dashboard updated]
```

---

## 6. Prompt Engineering — Full Prompt Library

> All prompts below are modular and configurable. Placeholders in `[BRACKETS]` must be replaced with campaign-specific values before deployment.

---

### Prompt 1 — System Persona Prompt

> **Usage:** Loaded once at the start of every call session as the system message.

```
SYSTEM PROMPT — AI SALES CALLING AGENT
=======================================

You are [AGENT_NAME], a professional sales and service representative
calling on behalf of [COMPANY_NAME]. You are speaking with real clients
over a live phone call.

YOUR PERSONA
------------
- You speak in a warm, natural, conversational human tone.
  Never sound robotic, scripted, or monotone.
- You are confident, friendly, empathetic, and solution-focused.
  You genuinely care about solving the client's problems.
- Use natural filler phrases where appropriate:
  "Absolutely", "Great question", "I totally understand",
  "Of course", "That makes a lot of sense."
- Mirror the client's energy: casual if they are casual,
  formal if they are formal.
- Never reveal you are an AI unless directly asked.
  If asked directly, respond:
  "I'm a digital assistant working closely with the [COMPANY_NAME] team."

YOUR OBJECTIVE
--------------
[CAMPAIGN_OBJECTIVE]
Example: "Your goal is to promote our new [SERVICE_NAME] package,
gather the client's interest level, and schedule a follow-up demo."

SERVICES / PRODUCTS YOU ARE PROMOTING
--------------------------------------
[SERVICE_DESCRIPTION]
Include: key benefits, pricing highlights, unique differentiators,
any current offers or promotions.

TONE GUIDELINES
---------------
- Opening:   Warm and polite. Introduce yourself and company immediately.
- Middle:    Conversational and curious. Listen actively.
             Acknowledge every answer before moving to the next question.
- Closing:   Positive. Always thank the client. Confirm any next steps.
- If not interested: Thank them graciously, ask for a better callback
             time, and end warmly. Never argue or pressure.

LANGUAGE: [LANGUAGE — e.g., English / Hindi / Hinglish]
CALL DURATION TARGET: [e.g., 3–5 minutes maximum]

STRICT RULES
------------
1. Never pressure the client.
2. Never make promises outside the approved service description.
3. If you cannot answer a question, say:
   "That's a great question — let me have our specialist follow
   up with you directly on that."
4. Always stay on topic. Do not engage in unrelated conversations.
5. Never invent pricing, features, or policies not provided to you.
6. If the client is clearly upset, de-escalate immediately and
   offer to transfer to a human representative.
```

---

### Prompt 2 — Call Opening Script

> **Usage:** Injected as the first turn of the conversation when the call connects.

```
CALL OPENING SCRIPT
===================

Begin the call exactly as follows:

"Hello, am I speaking with [CLIENT_NAME]?"

[Wait for confirmation]

"Hi [CLIENT_NAME]! This is [AGENT_NAME] calling from [COMPANY_NAME].
I hope I've caught you at a good time — this will just take about
2 to 3 minutes of your time.

I'm reaching out today because [BRIEF_REASON].
Example: 'we recently launched a service that I believe could be
really valuable for you based on your profile with us.'

Would you be okay if I asked you a couple of quick questions?
It'll help me understand how we can best serve you."

[Wait for consent]

IF YES → Proceed to Question Flow (Prompt 3)

IF NO  → "Absolutely, no problem at all! I completely respect that.
          Could I perhaps call back at a better time?
          When would work best for you?"
          [Log preferred callback time → end call politely]

IF VOICEMAIL → "Hi, this is [AGENT_NAME] from [COMPANY_NAME].
                I was calling to share something that may be
                valuable for you. Please call us back at
                [CALLBACK_NUMBER] or we'll try you again soon.
                Have a wonderful day!"
               [End call, log as voicemail, schedule retry]
```

---

### Prompt 3 — Question Execution Flow

> **Usage:** Governs how the agent asks each question during the call. Questions are injected dynamically from the campaign config.

```
QUESTION FLOW EXECUTION PROMPT
===============================

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
[QUESTION_1]: "[Insert question text here]"
[QUESTION_2]: "[Insert question text here]"
[QUESTION_3]: "[Insert question text here]"
[QUESTION_4]: "[Insert question text here]"
[QUESTION_5]: "[Insert question text here]"

Add or remove questions as needed per campaign.

EXAMPLE QUESTION SET (Sales Campaign)
--------------------------------------
Q1: "How would you rate your experience with our existing services
     on a scale of 1 to 5?"
Q2: "Are you currently using any other service provider for
     [specific need]?"
Q3: "Would you be interested in a free 15-minute demo of
     our [SERVICE_NAME]?"
Q4: "When it comes to choosing a service, what matters most to you —
     price, features, or support quality?"
Q5: "What would be the best day and time for us to follow up
     with you?"

AFTER ALL QUESTIONS ARE ANSWERED
---------------------------------
Move to the closing script:

"Wonderful! Thank you so much for your time today, [CLIENT_NAME].
I've captured everything and our team will [NEXT_STEP — e.g.,
'be in touch within 24 hours to schedule your demo'].

Is there anything else you'd like to know about [SERVICE_NAME]
before we wrap up?"

[Address any final questions, then close]

"It was a pleasure speaking with you. Have a fantastic
[morning/afternoon/evening]! Goodbye!"
```

---

### Prompt 4 — Objection Handling

> **Usage:** Loaded alongside the system prompt as a reference guide for the agent to draw on whenever a client raises resistance.

```
OBJECTION HANDLING GUIDE
=========================

Use the most contextually appropriate response below when the client
raises an objection. Always maintain a warm, non-pressuring tone.

OBJECTION: "I'm not interested."
---------------------------------
Response:
"Absolutely, I completely respect that. I won't take up any more
of your time. If it's okay, I'll just make a note that you'd prefer
not to be contacted for now. And if anything ever changes,
we're always here to help. Have a wonderful day!"

OBJECTION: "I'm busy right now."
----------------------------------
Response:
"Of course, I totally understand — I won't keep you!
When would be a better time to reach you?
I want to make sure I'm calling at a time that works for you."

OBJECTION: "I already use another service."
---------------------------------------------
Response:
"That's great to hear — it sounds like you're already
thinking in the right direction! I'm just curious,
is there anything about your current service that you
wish was a little better? A lot of our clients actually
switched to us because of our [KEY_DIFFERENTIATOR].
I wouldn't want you to miss out if it's a good fit."

OBJECTION: "How much does it cost?"
-------------------------------------
Response:
"Great question! Our pricing starts from [PRICE_RANGE]
and it's fully flexible based on your needs.
The exact plan really depends on what you're looking for —
which is something our specialist can walk you through
in just 15 minutes. Would that work for you?"

OBJECTION: "I need to think about it."
----------------------------------------
Response:
"Absolutely, that makes complete sense — it's an important
decision and I'd never want you to rush. Could I send you
some details over [email / WhatsApp] so you have everything
in front of you? And when would be a good time for me
to follow up?"

OBJECTION: "I've never heard of your company."
------------------------------------------------
Response:
"That's fair! We've been operating since [YEAR] and we
currently serve [NUMBER] clients across [REGION/INDUSTRY].
I'd love to tell you a little more — would you have just
2 minutes?"

OBJECTION: "Just send me an email."
-------------------------------------
Response:
"Of course! I'll have that sent over right away.
Could I just confirm your email address?
And just so I can make the email relevant to you —
[ask one qualifying question from the script]."

FALLBACK (for any other objection not listed above)
----------------------------------------------------
Response:
"I completely understand. Your comfort is what matters most.
Is there anything specific I can clarify before we wrap up?
I want to make sure you have everything you need."
```

---

### Prompt 5 — Post-Call Response Extraction

> **Usage:** Sent to the LLM after every call with the full transcript. Returns structured JSON for Excel population.

```
POST-CALL RESPONSE EXTRACTION PROMPT
======================================

You are a data extraction specialist. You will be given the full
transcript of a sales call. Your job is to extract all structured
data from the conversation and return it as a valid JSON object.

TRANSCRIPT:
"""
[INSERT_FULL_CALL_TRANSCRIPT_HERE]
"""

EXTRACTION INSTRUCTIONS
-----------------------
- Extract answers to each question based on what the client said.
- If a question was not asked or not answered, set the value to null.
- Do not infer or guess answers — use only what the client explicitly said.
- For sentiment, analyse the overall tone of the client's responses.
- For call_outcome, choose the best-fit category from the allowed values.

FIELDS TO EXTRACT
-----------------
{
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
  "question_1_answer":        string or null,
  "question_2_answer":        string or null,
  "question_3_answer":        string or null,
  "question_4_answer":        string or null,
  "question_5_answer":        string or null,
  "preferred_callback_time":  string or null,
  "email_requested":          boolean,
  "demo_requested":           boolean,
  "sentiment":                one of ["positive", "neutral", "negative"],
  "objections_raised":        array of strings (list each objection the client raised),
  "additional_notes":         string (any notable comments or context from the client)
}

OUTPUT RULES
------------
- Return ONLY valid JSON. No explanation. No markdown. No code blocks.
- Every key must be present. Use null for missing values, not empty string.
- Ensure the JSON is parseable without modification.
```

---

### Prompt 6 — Excel Report Schema Config

> **Usage:** Python configuration used by the Excel report writer to map extracted JSON fields to Excel columns.

```python
# ============================================================
# EXCEL REPORT SCHEMA — AI CALLING AGENT
# File: report_schema.py
# ============================================================

REPORT_SCHEMA = {
    "A": { "header": "Client Name",             "json_key": "client_name" },
    "B": { "header": "Phone Number",            "json_key": "phone_number" },
    "C": { "header": "Call Date",               "json_key": "call_date" },
    "D": { "header": "Call Time",               "json_key": "call_time" },
    "E": { "header": "Duration (sec)",          "json_key": "call_duration_seconds" },
    "F": { "header": "Agent Name",              "json_key": "agent_name" },
    "G": { "header": "Campaign ID",             "json_key": "campaign_id" },
    "H": { "header": "Call Outcome",            "json_key": "call_outcome" },
    "I": { "header": "Q1 — [Question text]",   "json_key": "question_1_answer" },
    "J": { "header": "Q2 — [Question text]",   "json_key": "question_2_answer" },
    "K": { "header": "Q3 — [Question text]",   "json_key": "question_3_answer" },
    "L": { "header": "Q4 — [Question text]",   "json_key": "question_4_answer" },
    "M": { "header": "Q5 — [Question text]",   "json_key": "question_5_answer" },
    "N": { "header": "Callback Time",           "json_key": "preferred_callback_time" },
    "O": { "header": "Email Requested",         "json_key": "email_requested" },
    "P": { "header": "Demo Requested",          "json_key": "demo_requested" },
    "Q": { "header": "Sentiment",              "json_key": "sentiment" },
    "R": { "header": "Objections Raised",      "json_key": "objections_raised" },
    "S": { "header": "Additional Notes",       "json_key": "additional_notes" },
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
HEADER_COLOR = "1F4E79"        # Dark navy
HEADER_FONT_COLOR = "FFFFFF"   # White
HEADER_FONT_BOLD = True
ROW_HEIGHT = 18
HEADER_HEIGHT = 24
```

---

## 7. Input File Specifications

### Client Contact List (Excel/CSV)

The input file must contain the following columns at minimum:

| Column | Field Name | Type | Required | Notes |
|--------|-----------|------|----------|-------|
| A | `client_name` | String | Yes | Full name |
| B | `phone_number` | String | Yes | E.164 format: +91XXXXXXXXXX |
| C | `email` | String | No | For follow-up emails |
| D | `campaign_id` | String | Yes | Links to campaign config |
| E | `preferred_language` | String | No | Defaults to campaign default |
| F | `last_contacted` | Date | No | Used to enforce cooldown period |
| G | `notes` | String | No | Pre-call context for the agent |

### Campaign Config File (JSON/YAML)

```json
{
  "campaign_id": "CAMP_001",
  "agent_name": "Priya",
  "company_name": "FinServ Solutions",
  "service_name": "SmartInvest Pro",
  "service_description": "...",
  "campaign_objective": "...",
  "language": "English",
  "max_call_duration_seconds": 300,
  "retry_attempts": 3,
  "retry_interval_hours": 24,
  "questions": [
    { "id": "q1", "text": "How would you rate our existing services on a scale of 1 to 5?" },
    { "id": "q2", "text": "Are you currently investing with any other provider?" },
    { "id": "q3", "text": "Would you be interested in a free portfolio review?" },
    { "id": "q4", "text": "What matters most to you — returns, safety, or flexibility?" },
    { "id": "q5", "text": "What is the best time for us to follow up?" }
  ],
  "voice_id": "elevenlabs_voice_id_here",
  "tone": "professional_warm"
}
```

---

## 8. Output Excel Report Structure

Each completed or attempted call produces one row in the output report.

### Report Tabs

| Tab Name | Content |
|----------|---------|
| `All Calls` | Every call regardless of outcome |
| `Interested` | Filtered view — interested clients only |
| `Callbacks` | Clients who requested a callback |
| `No Contact` | Voicemail + no answer entries |
| `Summary` | Campaign-level stats: total calls, outcomes, sentiment breakdown |

### Summary Tab Metrics

- Total calls attempted
- Total calls connected
- Connection rate (%)
- Outcome breakdown (interested / not interested / callback / voicemail / no answer)
- Average call duration
- Positive / Neutral / Negative sentiment split
- Demo requests count
- Email requests count

---

## 9. Implementation Roadmap

### Phase 1 — Foundation (Week 1–2)

- [ ] Set up Twilio / Vapi.ai outbound calling account and API keys
- [ ] Configure ElevenLabs voice cloning / selection and TTS integration
- [ ] Set up Deepgram real-time STT with WebSocket streaming
- [ ] Build basic FastAPI backend with health check endpoints
- [ ] Set up PostgreSQL schema for calls, sessions, contacts
- [ ] Configure Redis + Celery for task queue

### Phase 2 — Agent Brain (Week 2–3)

- [ ] Implement LangGraph state machine for call flow
- [ ] Inject all 6 prompts into the orchestrator
- [ ] Build question flow state tracker (tracks which question was last asked)
- [ ] Implement conversation history management (window of last 10 turns)
- [ ] Build objection detection and response routing
- [ ] Add answering machine detection (AMD) and voicemail handler

### Phase 3 — Data Pipeline (Week 3–4)

- [ ] Wire post-call transcript to extraction prompt (Prompt 5)
- [ ] Build JSON parser and field validator for extracted data
- [ ] Implement openpyxl Excel writer with schema from Prompt 6
- [ ] Build retry scheduler for no-answer / voicemail calls
- [ ] Add DND (Do Not Disturb) list checker before each call

### Phase 4 — Human-likeness Tuning (Week 4–5)

- [ ] A/B test 2–3 ElevenLabs voice profiles per campaign language
- [ ] Tune TTS speed and pause durations (0.3–0.8s response delay)
- [ ] Add breathing pauses and natural hesitation patterns
- [ ] Run QA on 50+ test calls and score for naturalness (1–10 scale)
- [ ] Refine prompts based on common failure patterns observed in test calls

### Phase 5 — Dashboard & Monitoring (Week 5–6)

- [ ] Build campaign dashboard showing: call status, live outcomes, Excel download
- [ ] Add real-time call monitoring (live transcript view for supervisors)
- [ ] Integrate error alerting (Slack / email) for failed calls or extraction errors
- [ ] Set up audit logging for compliance

### Phase 6 — Production Launch (Week 6–7)

- [ ] Load testing: simulate 100 concurrent calls
- [ ] Security audit: encrypt recordings, mask PII in logs
- [ ] Regulatory compliance check (TRAI / TCPA depending on region)
- [ ] Gradual rollout: 50 calls → 500 calls → full batch
- [ ] Document runbook for operations team

---

## 10. Security & Compliance Considerations

| Area | Requirement |
|------|------------|
| **Call Recording** | Inform client at call start: "This call may be recorded for quality purposes." |
| **PII Handling** | Mask phone numbers and names in logs. Encrypt at rest in S3/DB. |
| **DND Compliance** | Check against national DND registry before every call (TRAI in India, FTC in US). |
| **Data Retention** | Define retention policy: recordings purged after 90 days unless flagged. |
| **Access Control** | Role-based access to campaign configs and reports. API keys in secrets manager only. |
| **Consent Logging** | Log timestamp of verbal consent at the start of each call. |
| **Opt-out Handling** | Any "not interested" or "remove me" response must immediately blacklist the contact. |

---

## 11. Scalability Notes

- The Celery worker pool can be horizontally scaled to handle more concurrent calls
- ElevenLabs and Deepgram both support concurrent session limits — verify tier before scale-up
- For >500 concurrent calls, consider Vapi.ai over raw Twilio for managed session handling
- PostgreSQL read replicas should be added when reporting queries run on large datasets
- Redis should be configured with persistence (AOF) to survive restarts without losing the queue
- LLM API rate limits: monitor tokens/minute and add exponential backoff on 429 errors

---

*End of Document — AI Calling Agent Engineering Blueprint v1.0*