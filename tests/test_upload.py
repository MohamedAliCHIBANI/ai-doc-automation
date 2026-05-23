from tests.conftest import make_token

TXT_FILE = ("test.txt", b"Hello world content", "text/plain")


def test_upload_anonymous_new_session_succeeds(client):
    response = client.post(
        "/upload",
        files={"file": TXT_FILE},
        headers={"x-session-id": "new-session-abc"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "analysis" in data
    assert data["requires_auth"] is True


def test_upload_anonymous_used_session_returns_401(client_session_used):
    response = client_session_used.post(
        "/upload",
        files={"file": TXT_FILE},
        headers={"x-session-id": "already-used-session"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "auth_required"


def test_upload_no_auth_no_session_returns_401(client):
    response = client.post("/upload", files={"file": TXT_FILE})
    assert response.status_code == 401


def test_upload_authenticated_succeeds(client):
    response = client.post(
        "/upload",
        files={"file": TXT_FILE},
        headers={"authorization": f"Bearer {make_token()}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "analysis" in data
    assert "usage" in data
    assert "requires_auth" not in data


def test_upload_authenticated_at_limit_returns_403(client_at_limit):
    response = client_at_limit.post(
        "/upload",
        files={"file": TXT_FILE},
        headers={"authorization": f"Bearer {make_token()}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "upload_limit_reached"


def test_upload_unsupported_type_returns_400(client):
    response = client.post(
        "/upload",
        files={"file": ("doc.docx", b"data", "application/octet-stream")},
        headers={"x-session-id": "new-session-xyz"},
    )
    assert response.status_code == 400
