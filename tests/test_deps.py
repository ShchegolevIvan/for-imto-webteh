import json
import pytest
from fastapi import HTTPException
from starlette.requests import Request
from starlette.datastructures import Headers

from app import models
from app.deps import get_current_user, require_admin, require_verified_author


class DummyRedis:
    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def setex(self, key, ttl, value):
        self.store[key] = value


def make_request(auth_header: str | None):
    headers = {}
    if auth_header:
        headers["Authorization"] = auth_header

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/x",
        "headers": Headers(headers).raw,
    }
    return Request(scope)


def test_require_admin_denied():
    u = models.User(id=1, name="u", email="u@u", is_admin=False, is_verified_author=False)
    with pytest.raises(HTTPException) as e:
        require_admin(u)
    assert e.value.status_code == 403


def test_require_verified_author_denied():
    u = models.User(id=1, name="u", email="u@u", is_admin=False, is_verified_author=False)
    with pytest.raises(HTTPException) as e:
        require_verified_author(u)
    assert e.value.status_code == 403


def test_get_current_user_no_auth(db_session, monkeypatch):
    # без Authorization
    req = make_request(None)

    # jwt_decode не нужен, потому что упадем раньше
    with pytest.raises(HTTPException) as e:
        get_current_user(req, db_session, DummyRedis())
    assert e.value.status_code == 401


def test_get_current_user_from_redis_cache(db_session, monkeypatch):
    # подменим jwt_decode, чтобы не зависеть от реальных токенов
    monkeypatch.setattr("app.deps.jwt_decode", lambda token: {"type": "access", "sub": "123"})

    r = DummyRedis()
    cached = {
        "id": 123,
        "name": "cached",
        "email": "c@c",
        "is_verified_author": False,
        "is_admin": False,
        "avatar": None,
        "github_id": None,
        "github_login": None,
    }
    r.store["user:123"] = json.dumps(cached)

    req = make_request("Bearer whatever")
    user = get_current_user(req, db_session, r)
    assert user.id == 123
    assert user.email == "c@c"
