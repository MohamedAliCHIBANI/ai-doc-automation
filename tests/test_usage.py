from tests.conftest import make_token


def test_usage_no_auth_returns_401(client):
    response = client.get("/usage")
    assert response.status_code == 401


def test_usage_authenticated_returns_count(client):
    response = client.get(
        "/usage",
        headers={"authorization": f"Bearer {make_token()}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["used"] == 0
    assert data["limit"] == 10
    assert data["remaining"] == 10
