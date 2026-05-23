# DocMind — AI Document Automation

> Upload any document. Get instant AI-powered analysis.

DocMind is a full-stack application that extracts structured insights from **PDF**, **CSV**, and **TXT** files using OpenAI's GPT-4o-mini model. It returns a clean analysis including a summary, key points, sentiment, document type, and word count — all in seconds.

**Live demo:** [http://docanalyzer.dev/](http://docanalyzer.dev/)  
**API:** [https://ai-doc-automation.onrender.com](https://ai-doc-automation.onrender.com)

---

## Features

- **Multi-format support** — PDF (via pdfplumber), CSV (via pandas), and plain text
- **Structured AI analysis** — summary, key points, sentiment, document type, word count
- **REST API** — clean FastAPI backend, fully documented via `/docs`
- **Modern UI** — dark-mode single-page frontend with drag-and-drop upload
- **Dockerized** — ready to run anywhere with a single command
- **Cloud-deployed** — hosted on Render with zero configuration

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.10, FastAPI, Uvicorn |
| AI | OpenAI API (`gpt-4o-mini`) |
| Parsers | pdfplumber (PDF), pandas (CSV) |
| Frontend | Vanilla HTML / CSS / JavaScript |
| Container | Docker, Docker Compose |
| Hosting | Render (API), docanalyzer.dev (frontend) |

---

## Project Structure

```
ai-doc-automation/
├── app/
│   ├── main.py                  # FastAPI app, CORS, routes
│   └── services/
│       ├── file_loader.py       # PDF / CSV / TXT text extraction
│       └── ai_summarizer.py     # OpenAI prompt + JSON response parsing
├── index.html                   # Frontend (single-file SPA)
├── Dockerfile
├── docker-compose.yml
├── render.yaml
├── requirements.txt
└── .env                         # Local secrets (never committed)
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

**Response:**
```json
{
  "filename": "report.pdf",
  "analysis": {
    "Summary": "...",
    "Key Points": ["...", "...", "...", "...", "..."],
    "Document Type": "Financial Report",
    "Sentiment": "neutral",
    "Word Count": 1240
  }
}
```

**Error responses:**

| Status | Cause |
|--------|-------|
| `400` | Unsupported file type |
| `500` | Processing or OpenAI API failure |

Interactive API docs available at [`/docs`](https://ai-doc-automation.onrender.com/docs).

---

## Local Setup

### Prerequisites

- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys)

### 1. Clone and install

```bash
git clone https://github.com/your-username/ai-doc-automation.git
cd ai-doc-automation

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add your key:
# OPENAI_API_KEY=sk-...
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

## Deployment

The API is deployed on **Render** using the configuration in `render.yaml`.  
Set the `OPENAI_API_KEY` environment variable in your Render service dashboard — never commit it to the repository.

The frontend (`index.html`) can be hosted on any static hosting provider (Netlify, Vercel, GitHub Pages, etc.). Update the `API_URL` constant at the top of the script block to match your deployed API URL.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | Your OpenAI secret key |

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
