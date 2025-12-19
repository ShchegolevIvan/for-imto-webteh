from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_news_requires_auth():
    response = client.get("/news")
    assert response.status_code in (401, 403)


def test_create_news_unauthorized():
    response = client.post(
        "/news",
        json={
            "title": "hello",
            "text": "world",
            "author_id": 1,
        },
    )
    assert response.status_code in (401, 403)
