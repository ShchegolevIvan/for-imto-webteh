import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db import get_db, get_redis


class DummyRedis:
    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def setex(self, key, ttl, value):
        self.store[key] = value

    def set(self, key, value):
        self.store[key] = value

    def delete(self, key):
        self.store.pop(key, None)


@pytest.fixture()
def client(db_session):
    # ВАЖНО: подменяем get_db на sqlite-сессию из conftest
    app.dependency_overrides[get_db] = lambda: db_session

    dummy = DummyRedis()
    app.dependency_overrides[get_redis] = lambda: dummy

    c = TestClient(app)
    yield c, dummy

    app.dependency_overrides.clear()


def test_register_login_refresh_logout_flow(client):
    client, _redis = client

    r = client.post("/auth/register", json={"name": "A", "email": "a@a", "password": "123"})
    assert r.status_code in (200, 201)

    r = client.post("/auth/login", json={"email": "a@a", "password": "123"})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data and "refresh_token" in data
    refresh_token = data["refresh_token"]

    r = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert r.status_code == 200
    assert "access_token" in r.json()

    r = client.post("/auth/logout", json={"refresh_token": refresh_token})
    assert r.status_code == 200
