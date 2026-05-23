import os

# Set test env vars before any app module is imported so module-level
# code (OpenAI client init, JWT secret read) sees these values.
os.environ["OPENAI_API_KEY"] = "sk-test"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_JWT_SECRET"] = "test-jwt-secret-needs-at-least-32chars"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "test-role-key"

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from jose import jwt as jose_jwt

_TEST_SECRET = "test-jwt-secret-needs-at-least-32chars"
TEST_USER_ID = "user-test-123"

FAKE_ANALYSIS = (
    '{"Summary":"Test summary.","Key Points":["Point 1"],'
    '"Document Type":"TXT","Sentiment":"neutral","Word Count":5}'
)


def make_token(user_id: str = TEST_USER_ID) -> str:
    return jose_jwt.encode({"sub": user_id}, _TEST_SECRET, algorithm="HS256")


def _make_sb(upload_count: int = 0, session_used: bool = False) -> MagicMock:
    sb = MagicMock()

    def table_side_effect(name):
        m = MagicMock()
        if name == "upload_usage":
            m.select.return_value.eq.return_value.execute.return_value.data = (
                [{"count": upload_count}] if upload_count > 0 else []
            )
        elif name == "anonymous_sessions":
            m.select.return_value.eq.return_value.execute.return_value.data = (
                [{"used": session_used}] if session_used else []
            )
        m.insert.return_value.execute.return_value.data = []
        m.update.return_value.eq.return_value.execute.return_value.data = []
        return m

    sb.table.side_effect = table_side_effect
    return sb


def _make_openai_mock(content: str = FAKE_ANALYSIS) -> MagicMock:
    mock = MagicMock()
    mock.chat.completions.create.return_value.choices[0].message.content = content
    return mock


def _make_client(upload_count: int = 0, session_used: bool = False):
    # Import first so the names exist in their modules before we patch them.
    # Patch at the call site (usage_tracker) not the definition site (supabase_client),
    # because `from .supabase_client import get_supabase` binds a local name.
    import app.services.usage_tracker  # noqa: F401

    sb = _make_sb(upload_count=upload_count, session_used=session_used)
    ai = _make_openai_mock()
    with patch("app.services.usage_tracker.get_supabase", return_value=sb), \
         patch("app.services.ai_summarizer.client", ai):
        from app.main import app
        with TestClient(app) as c:
            yield c


@pytest.fixture
def client():
    yield from _make_client()


@pytest.fixture
def client_at_limit():
    yield from _make_client(upload_count=10)


@pytest.fixture
def client_session_used():
    yield from _make_client(session_used=True)
