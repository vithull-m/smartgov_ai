# SMARTGOV AI — Multilingual AI Government Scheme Agent

SMARTGOV AI is a comprehensive, production-grade citizen welfare assistant designed for Indian citizens. It features an intelligent multilingual AI agent that automatically detects typed and spoken languages, queries a verified government scheme database using deterministic rule evaluation, and synchronizes information from official government portals.

---

## 🌟 Key Features

1. **Automatic Multilingual Language Detection (No Dropdowns Required)**
   - Automatically detects user language from typed messages.
   - Native support for **Tamil (தமிழ்)**, **English**, **Hindi (हिंदी)**, and romanized mixed languages (**Tanglish / Tamil-English code-switching**).
   - Preserves user language throughout conversation.
   - Preserves official scheme titles and application URLs accurately in all translations.
   - Built-in Voice Input (Microphone) with automatic speech recognition and speech output.

2. **Hosted Cloud AI Agent with Fallback Reasoning**
   - Configurable AI reasoning provider via environment variables (`OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`).
   - Acts as reasoning agent executing 8 backend Python tools:
     - `detect_language`
     - `search_schemes`
     - `get_scheme_details`
     - `check_eligibility`
     - `get_required_documents`
     - `get_application_steps`
     - `get_scheme_source`
     - `check_update_status`
   - Does not invent scheme facts, income thresholds, or rules.
   - Graceful fallback reasoning engine when API keys are not supplied.

3. **Deterministic 4-Status Eligibility Engine**
   - Strictly rule-based (no hallucinated eligibility assessments).
   - Returns one of 4 deterministic statuses:
     - `likely_eligible` (all rules passed)
     - `not_eligible` (one or more rules failed)
     - `needs_more_information` (missing user profile attributes)
     - `unverified_scheme_data` (flagged unverified records)
   - Evaluates: Age, Annual Income, State/Residence, Occupation, Student status, Farmer status, Gender, Category, Disability.
   - Formulates precise follow-up questions only for missing information.

4. **Trusted Provenance & Scheme Update Service**
   - Tracks `government_level`, `source_url`, `source_status`, `last_checked_at`, and `last_verified_at` for every scheme.
   - Scheduled & administrative updater syncing trusted sources (e.g. `myscheme.gov.in`, `scholarships.gov.in`, `pmkisan.gov.in`).
   - Duplicate prevention with field-level audit logs in `scheme_update_history`.

5. **Production-Ready Interactive Voice Response (IVRS) Helpline**
   - Simulated interactive phone keypad and dialer (`/ivr`) in the citizen portal.
   - Multilingual audio voice prompts & menus in **Tamil (தமிழ்)**, **English**, and **Hindi (हिंदी)**.
   - DTMF touch-tone navigation (Press 1 for Agriculture, 2 for Scholarships, 3 for Women Welfare, 4 for Healthcare, 5 for voice speech).
   - Generates industry-standard **TwiML XML** webhooks compatible with Twilio, Exotel, or any cloud PBX gateway.
   - Natural speech queries: citizens can speak their question over the phone, and the IVRS engine queries the scheme database and synthesizes concise conversational voice responses.
   - Complete call session logging with duration, language, DTMF trace, and scheme history.


---

## 🛠️ Technology Stack

- **Frontend:** React 18, Vite, Tailwind CSS, Web Speech API
- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2
- **Database:** SQLite (`smartgov_ai.db` default for rapid local demo) / MySQL (production ready)
- **Testing:** Pytest, HTTPX, FastAPI TestClient

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- Node.js 18+ (Node.js 24 installed)
- Git

---

### 2. Backend Setup

1. **Navigate to the backend directory:**
   ```powershell
   cd backend
   ```

2. **Activate the virtual environment:**
   ```powershell
   # Windows PowerShell
   ..\.venv\Scripts\Activate.ps1
   # Or directly run with .venv\Scripts\python.exe
   ```

3. **Configure Environment Variables:**
   Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```
   Edit `.env` if you wish to configure a cloud AI provider:
   ```env
   DATABASE_URL=sqlite:///./smartgov_ai.db
   SECRET_KEY=your-secret-key-at-least-32-characters
   OPENAI_API_KEY=sk-your-openai-or-groq-key
   OPENAI_BASE_URL=https://api.openai.com/v1
   OPENAI_MODEL=gpt-4o-mini
   ADMIN_API_KEY=smartgov-admin-secure-key
   ```
   *(Note: If `OPENAI_API_KEY` is left blank, SmartGov AI will automatically operate in offline verified knowledge mode).*

4. **Verify / Initialize Database:**
   The database automatically creates any missing tables and executes safe schema migrations on startup:
   ```powershell
   python seed_schemes.py
   ```

5. **Start FastAPI Backend Server:**
   ```powershell
   uvicorn app.main:app --reload --port 8000
   ```
   - Swagger Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Health Check: [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

### 3. Frontend Setup

1. **Navigate to the frontend directory:**
   ```powershell
   cd frontend
   ```

2. **Install dependencies:**
   ```powershell
   npm install
   ```

3. **Start the Frontend Development Server:**
   ```powershell
   npm run dev
   ```
   - Open browser: [http://localhost:5173](http://localhost:5173)

---

## 🧪 Automated Testing

Run the comprehensive pytest suite covering language detection, eligibility rules, agent tools, updates, and API endpoints:

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest tests/test_agent_system.py -v
```

All 13 test scenarios pass without requiring paid API credits.

---

## 📡 API Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chatbot` | Multilingual agent chat with auto language detection & tool execution |
| `POST` | `/api/eligibility/check` | Deterministic eligibility check with custom user profile |
| `GET` | `/api/eligibility/check/{id}` | Check logged-in user eligibility for specific scheme |
| `GET` | `/api/schemes` | Filter and list government schemes |
| `GET` | `/api/schemes/{id}` | Full scheme details, required documents, and application steps |
| `GET` | `/api/updates/status` | Current scheme synchronization and verification status |
| `POST` | `/api/updates/sync` | Admin-triggered update check against official portals |
| `GET` | `/api/health` | Backend and database connectivity health check |

---

## 🔒 Security & Privacy

- **Data Minimization:** SmartGov AI only prompts for fields required to calculate scheme eligibility. Sensitive identifiers like Aadhaar numbers or bank accounts are never collected or transmitted in the chat interface.
- **No Hallucinated Decisions:** Preliminary eligibility assessments are strictly separated from government approval.
- **Admin Access Control:** Update operations are secured via administrative keys (`X-Admin-Key`).
