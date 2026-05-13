# 🤖 AI Calling Agent

> **Autonomous AI Voice Calling Agent for Sales & Service Promotion**

An AI-powered autonomous voice calling agent that reads client contacts, dials them via cloud telephony (Vapi.ai), conducts natural sales conversations using GPT-4.1, and auto-generates structured Excel reports.

---

## 🏗️ Architecture

```
INPUT LAYER          →    ORCHESTRATOR    →    VOICE AI LAYER    →    TELEPHONY    →    OUTPUT
(Excel/CSV + Config)      (FastAPI +           (GPT-4.1 +             (Vapi.ai)         (Excel Reports
                          LangGraph)            ElevenLabs +                             + Dashboard)
                                               Deepgram)
```

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **LLM Brain** | GPT-4.1 (OpenAI) |
| **Text-to-Speech** | ElevenLabs Turbo v2.5 |
| **Speech-to-Text** | Deepgram Nova-2 |
| **Telephony** | Vapi.ai (primary) / Twilio (fallback) |
| **Orchestration** | LangGraph (Python) |
| **Backend** | FastAPI (Python 3.12+) |
| **Task Queue** | Redis + Celery |
| **Database** | PostgreSQL 16 |
| **Report Output** | openpyxl |
| **Deployment** | Docker + Docker Compose |

---

## 📁 Project Structure

```
CallingAgent/
├── backend/
│   ├── app/
│   │   ├── api/            # REST API routes (campaigns, contacts, calls, reports, webhooks)
│   │   ├── graph/          # LangGraph state machine (state, nodes, edges, builder)
│   │   ├── models/         # SQLAlchemy ORM models (Campaign, Contact, CallSession, CallLog)
│   │   ├── prompts/        # 6 prompt templates from the engineering blueprint
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── services/       # Business logic (orchestrator, telephony, extraction, reporting)
│   │   ├── tasks/          # Celery background tasks (calls, batches, reports)
│   │   ├── config.py       # Pydantic Settings configuration
│   │   ├── database.py     # Async SQLAlchemy engine
│   │   └── main.py         # FastAPI app entry point
│   ├── alembic/            # Database migrations
│   ├── docker-compose.yml  # PostgreSQL + Redis + App + Workers
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
├── sample_data/            # Sample campaign config & contacts
└── project.md              # Engineering blueprint
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- API Keys: OpenAI, Vapi.ai, ElevenLabs, Deepgram

### 1. Clone & Configure

```bash
cd CallingAgent/backend
cp .env.example .env
# Edit .env with your actual API keys
```

### 2. Start Infrastructure

```bash
docker-compose up -d postgres redis
```

### 3. Install Dependencies

```bash
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 4. Run the Server

```bash
uvicorn app.main:app --reload --port 8000
```

### 5. Start Celery Worker

```bash
celery -A app.tasks.celery_app worker --loglevel=info -Q default,calls,reports
```

### 6. Open API Docs

Visit `http://localhost:8000/docs` for the interactive Swagger UI.

---

## 📞 How It Works

1. **Create a Campaign** — Define agent name, company, service, questions, and voice settings
2. **Upload Contacts** — Upload an Excel/CSV file with client contact data
3. **Launch Calls** — Initiate single calls or batch campaigns
4. **Vapi.ai handles the call** — Real-time voice conversation with GPT-4.1 + ElevenLabs + Deepgram
5. **Webhooks process events** — Call started, transcript updates, call ended
6. **Post-call extraction** — GPT-4.1 extracts structured JSON from the transcript
7. **Excel report generated** — Color-coded report with 5 tabs and summary metrics

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/campaigns/` | Create a campaign |
| `GET` | `/api/v1/campaigns/` | List all campaigns |
| `GET` | `/api/v1/campaigns/{id}` | Get campaign details |
| `POST` | `/api/v1/contacts/{campaign_id}/upload` | Upload contacts file |
| `POST` | `/api/v1/calls/initiate` | Start a single call |
| `POST` | `/api/v1/calls/batch` | Launch batch campaign |
| `GET` | `/api/v1/calls/status/{session_id}` | Check call status |
| `POST` | `/api/v1/reports/generate` | Generate Excel report |
| `GET` | `/api/v1/reports/download/{filename}` | Download report |
| `POST` | `/api/v1/webhooks/vapi` | Vapi.ai webhook handler |

---

## 🧠 Prompt System

The agent uses 6 modular prompts from the engineering blueprint:

| # | Prompt | Purpose |
|---|--------|---------|
| 1 | System Persona | Agent identity, persona, objectives, strict rules |
| 2 | Call Opening | Introduction script with consent flow |
| 3 | Question Flow | Sequential question asking with acknowledgment |
| 4 | Objection Handling | 7 objection responses + fallback |
| 5 | Post-Call Extraction | Transcript → structured JSON (18 fields) |
| 6 | Report Schema | Excel column mapping with color coding |

---

## 📋 License

This project is proprietary software. All rights reserved.
