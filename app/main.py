import os
import httpx
from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from dotenv import load_dotenv

from app.services.file_loader import load_file
from app.services.ai_summarizer import summarize
from app.services.usage_tracker import (
    get_user_count,
    increment_user_count,
    is_session_used,
    mark_session_used,
    MAX_UPLOADS,
)

load_dotenv()

app = FastAPI(
    title="AI Document Automation API",
    description="Upload PDF, CSV, and TXT and get AI-powered summaries",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_JWT_SECRET   = os.getenv("SUPABASE_JWT_SECRET", "")
_SUPABASE_URL = os.getenv("SUPABASE_URL", "")
_jwks_cache: dict | None = None


def _get_jwks() -> dict:
    """Fetch and cache Supabase public JWKS (used for ECC tokens)."""
    global _jwks_cache
    if _jwks_cache is None:
        url = f"{_SUPABASE_URL}/auth/v1/.well-known/jwks.json"
        resp = httpx.get(url, timeout=10)
        resp.raise_for_status()
        _jwks_cache = resp.json()
    return _jwks_cache


def _get_user_id(authorization: str | None) -> str | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization[7:]

    try:
        header = jwt.get_unverified_header(token)
        alg = header.get("alg", "HS256")
        kid = header.get("kid")

        if alg == "HS256":
            # Legacy shared-secret key
            payload = jwt.decode(
                token,
                _JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
        else:
            # ECC / RSA key — verify via JWKS
            keys = _get_jwks().get("keys", [])
            candidates = [k for k in keys if k.get("kid") == kid] or keys

            payload = None
            last_err: Exception = JWTError("No matching key found")
            for key_data in candidates:
                try:
                    payload = jwt.decode(
                        token,
                        key_data,
                        algorithms=[alg],
                        options={"verify_aud": False},
                    )
                    break
                except JWTError as exc:
                    last_err = exc

            if payload is None:
                raise last_err

        return payload.get("sub")

    except JWTError:
        raise HTTPException(status_code=401, detail="invalid_token")


@app.get("/")
def health_check():
    return {"status": "ok", "message": "AI Document Automation API is running"}


@app.get("/usage")
def get_usage(authorization: str = Header(None)):
    user_id = _get_user_id(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="auth_required")
    count = get_user_count(user_id)
    return {"used": count, "limit": MAX_UPLOADS, "remaining": MAX_UPLOADS - count}


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    authorization: str = Header(None),
    x_session_id: str = Header(None),
):
    user_id = _get_user_id(authorization)

    try:
        if user_id:
            count = get_user_count(user_id)
            if count >= MAX_UPLOADS:
                raise HTTPException(status_code=403, detail="upload_limit_reached")

            content = await file.read()
            text = load_file(filename=file.filename, content=content)
            result = summarize(text=text, doc_type=file.filename.rsplit(".", 1)[-1].upper())
            new_count = increment_user_count(user_id)

            return {
                "filename": file.filename,
                "analysis": result,
                "usage": {"used": new_count, "limit": MAX_UPLOADS},
            }

        else:
            if not x_session_id or is_session_used(x_session_id):
                raise HTTPException(status_code=401, detail="auth_required")

            content = await file.read()
            text = load_file(filename=file.filename, content=content)
            result = summarize(text=text, doc_type=file.filename.rsplit(".", 1)[-1].upper())
            mark_session_used(x_session_id)

            return {
                "filename": file.filename,
                "analysis": result,
                "requires_auth": True,
                "usage": {"used": 1, "limit": 1},
            }

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
