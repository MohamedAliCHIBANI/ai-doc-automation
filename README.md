# ai-doc-automation

AI Document Automation API.

## Setup

Prerequisites: Python 3.10+, and an OpenAI API key.

1) Create and activate a virtual environment

2) Install dependencies

pip install -r requirements.txt

3) Create a .env file with:

OPENAI_API_KEY=your_key_here

## Run (local)

uvicorn app.main:app --reload

The API will be available at http://127.0.0.1:8000

## Docker

docker compose up --build

The container exposes port 8000 and reads environment variables from .env.

## Structure

- `app/api/`
- `app/core/`
- `app/services/`
- `app/main.py`
- `tests/`
- `docker-compose.yml`
- `Dockerfile`
- `requirements.txt`
