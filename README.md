# DocMind — AI Document Automation

> Upload any document. Get instant AI-powered analysis.

DocMind is a full-stack application that extracts structured insights from **PDF**, **CSV**, and **TXT** files using OpenAI's GPT-4o-mini model. It returns a clean analysis including a summary, key points, sentiment, document type, and word count — all in seconds.

**Live demo:** [http://docanalyzer.dev/](http://docanalyzer.dev/)  
**API:** [https://ai-doc-automation.onrender.com](https://ai-doc-automation.onrender.com)

---

## Features

- **Multi-format support** — PDF (via pdfplumber), CSV (via pandas), and plain text
- **Structured AI analysis** — summary, key points, sentiment, document type, word count
- **Authentication** — email/password and Google OAuth via Supabase; JWT verification on every request
- **Usage tiers** — anonymous users get 1 free analysis (session-tracked); authenticated users get 10 lifetime analyses
- **REST API** — clean FastAPI backend, fully documented via `/docs`
- **Modern UI** — dark-mode single-page frontend with drag-and-drop upload, auth modal, and live usage counter
- **Dockerized** — ready to run anywhere with a single command
- **CI pipeline** — pytest suite with coverage runs on every push via GitHub Actions
- **Cloud-deployed** — API hosted on Vercel (serverless Python)

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.10, FastAPI, Uvicorn |
| AI | OpenAI API (`gpt-4o-mini`) |
| Parsers | pdfplumber (PDF), pandas (CSV) |
| Auth | Supabase (email/password + Google OAuth), python-jose |
| Frontend | Vanilla HTML / CSS / JavaScript |
| Container | Docker, Docker Compose |
| CI | GitHub Actions, pytest, pytest-cov |
| Hosting | Vercel (API), docanalyzer.dev (frontend) |

---

## Project Structure

```
ai-doc-automation/
├── app/
│   ├── main.py                  # FastAPI app, CORS, JWT verification, routes
│   └── services/
│       ├── file_loader.py       # PDF / CSV / TXT text extraction
│       ├── ai_summarizer.py     # OpenAI prompt + JSON response parsing
│       ├── supabase_client.py   # Supabase admin client
│       └── usage_tracker.py     # Per-user and per-session upload counts
├── tests/
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_upload.py
│   ├── test_usage.py
│   ├── test_file_loader.py
│   └── test_ai_summarizer.py
├── .github/workflows/ci.yml    # GitHub Actions CI
├── index.html                   # Frontend (single-file SPA)
├── Dockerfile
├── docker-compose.yml
├── vercel.json                  # Vercel deployment config
├── .python-version              # Python version used by Vercel
├── requirements.txt
├── requirements-dev.txt
└── .env.example                 # Environment variable template
```

---

## API Reference

### `GET /`
Health check.

```json
{ "status": "ok", "message": "AI Document Automation API is running" }
```

### `POST /upload`
Upload a document and receive an AI analysis.

**Request:** `multipart/form-data` with a `file` field (`.pdf`, `.csv`, or `.txt`)

**Headers (optional):**

| Header | Description |
|--------|-------------|
| `Authorization: Bearer <token>` | Supabase JWT for authenticated users (10 uploads lifetime) |
| `X-Session-Id: <uuid>` | Anonymous session ID (1 free upload per session) |

**Response (authenticated):**
```json
{
  "filename": "report.pdf",
  "analysis": {
    "Summary": "...",
    "Key Points": ["...", "...", "...", "...", "..."],
    "Document Type": "Financial Report",
    "Sentiment": "neutral",
    "Word Count": 1240
  },
  "usage": { "used": 3, "limit": 10 }
}
```

**Response (anonymous — first use):**
```json
{
  "filename": "report.pdf",
  "analysis": { ... },
  "requires_auth": true,
  "usage": { "used": 1, "limit": 1 }
}
```

**Error responses:**

| Status | Detail | Cause |
|--------|--------|-------|
| `400` | — | Unsupported file type |
| `401` | `auth_required` | No valid session or token provided |
| `401` | `invalid_token` | Malformed or expired JWT |
| `403` | `upload_limit_reached` | Authenticated user hit the 10-upload cap |
| `500` | — | Processing or OpenAI API failure |

### `GET /usage`
Returns the current upload count for an authenticated user.

**Headers:** `Authorization: Bearer <token>` (required)

```json
{ "used": 3, "limit": 10, "remaining": 7 }
```

Interactive API docs available at [`/docs`](https://ai-doc-automation.onrender.com/docs).

---

## Local Setup

### Prerequisites

- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys)
- A [Supabase](https://supabase.com) project with `upload_usage` and `anonymous_sessions` tables

### 1. Clone and install

```bash
git clone https://github.com/MohamedAliCHIBANI/ai-doc-automation.git
cd ai-doc-automation

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Fill in the values below
```

### 3. Run the API

```bash
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`.  
Open `index.html` in your browser or point the frontend `API_URL` to `http://127.0.0.1:8000`.

---

## Docker

```bash
docker compose up --build
```

The container exposes port `8000` and reads environment variables from `.env`.

---

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v --cov=app --cov-report=term-missing
```

Tests mock the OpenAI and Supabase clients so no live credentials are needed. The full suite also runs on every push to `main` via GitHub Actions.

---

## Deployment

The API is deployed on **Vercel**. `app/main.py` exposes the FastAPI `app` instance, which Vercel detects automatically. `vercel.json` sets the function timeout and which files are left out of the bundle.

1. Import the GitHub repository in the Vercel dashboard (**Add New → Project**). Leave the framework preset on **FastAPI** and the root directory on `./`.
2. Under **Settings → Environment Variables**, add `OPENAI_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` and `SUPABASE_JWT_SECRET`. Never commit secrets to the repository.
3. Deploy. Every push to `main` triggers a production deployment, and pull requests get preview URLs.

You can also deploy with the CLI: `npm i -g vercel`, then `vercel` (preview) or `vercel --prod`.

> **Limit:** Vercel functions accept request bodies up to **4.5 MB**, so the frontend rejects files larger than 4 MB.

The frontend (`index.html`) is a static page served via GitHub Pages at `docanalyzer.dev`. Point the `API_URL` constant at the top of its script block at your Vercel deployment URL.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | Your OpenAI secret key |
| `SUPABASE_URL` | Yes | Your Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Supabase service-role key (backend only) |
| `SUPABASE_JWT_SECRET` | Yes | Supabase JWT secret for token verification |

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push and open a pull request

---

## License

MIT — feel free to use, modify, and distribute.

---

Built by [Mohamed Ali Chibani](mailto:mohamedali.chibani@enicar.ucar.tn)
