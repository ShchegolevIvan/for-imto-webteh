import time
import pytest

from app.security import (
    hash_password,
    verify_password,
    jwt_encode,
    jwt_decode,
    new_access_token,
    new_refresh_token,
)


def test_password_hash_and_verify():
    h = hash_password("secret123")
    assert verify_password("secret123", h) is True
    assert verify_password("wrong", h) is False


def test_jwt_encode_decode_roundtrip():
    payload = {"iss": "news-api", "sub": "1", "exp": int(time.time()) + 60}
    token = jwt_encode(payload)
    decoded = jwt_decode(token)
    assert decoded["sub"] == "1"
    assert decoded["iss"] == "news-api"


def test_jwt_decode_bad_signature():
    payload = {"iss": "news-api", "sub": "1", "exp": int(time.time()) + 60}
    token = jwt_encode(payload)
    # ломаем токен
    bad = token[:-1] + ("a" if token[-1] != "a" else "b")
    with pytest.raises(Exception):
        jwt_decode(bad)


def test_jwt_decode_expired():
    payload = {"iss": "news-api", "sub": "1", "exp": int(time.time()) - 1}
    token = jwt_encode(payload)
    with pytest.raises(Exception):
        jwt_decode(token)


def test_access_and_refresh_token_types():
    access = new_access_token(1, is_admin=False, is_verified_author=False)
    a = jwt_decode(access)
    assert a["type"] == "access"
    assert a["sub"] == "1"

    refresh, jti, exp_dt = new_refresh_token(1)
    r = jwt_decode(refresh)
    assert r["type"] == "refresh"
    assert r["jti"] == jti
    assert int(exp_dt.timestamp()) == r["exp"]
