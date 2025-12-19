from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_users_requires_auth():
    response = client.get("/users")
    assert response.status_code in (401, 403)


def test_create_user_unauthorized():
    response = client.post(
        "/users",
        json={
            "name": "api_user",
            "email": "api@example.com",
        },
    )
    # без токена ожидаем отказ
    assert response.status_code in (401, 403)
