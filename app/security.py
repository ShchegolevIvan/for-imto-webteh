import os, hmac, hashlib, base64, json, time, uuid
from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher

JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret")
JWT_ISS = os.getenv("JWT_ISS", "news-api")
ACCESS_TTL = int(os.getenv("JWT_ACCESS_TTL_SECONDS", "900"))
REFRESH_TTL = int(os.getenv("JWT_REFRESH_TTL_SECONDS", "2592000"))

ph = PasswordHasher()

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    try:
        ph.verify(password_hash, password)
        return True
    except Exception:
        return False

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

def _b64url_json(obj: dict) -> str:
    return _b64url(json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))

def _sign(data: bytes) -> str:
    return _b64url(hmac.new(JWT_SECRET.encode("utf-8"), data, hashlib.sha256).digest())

def jwt_encode(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    h = _b64url_json(header)
    p = _b64url_json(payload)
    sig = _sign(f"{h}.{p}".encode("ascii"))
    return f"{h}.{p}.{sig}"

def jwt_decode(token: str) -> dict:
    h, p, s = token.split(".")
    exp_sig = _sign(f"{h}.{p}".encode("ascii"))
    if not hmac.compare_digest(s, exp_sig):
        raise ValueError("bad signature")
    payload = json.loads(base64.urlsafe_b64decode(p + "==").decode("utf-8"))
    if payload.get("iss") != JWT_ISS:
        raise ValueError("bad iss")
    if "exp" in payload and int(payload["exp"]) < int(time.time()):
        raise ValueError("expired")
    return payload

def new_access_token(user_id: int, is_admin: bool, is_verified_author: bool) -> str:
    now = int(time.time())
    payload = {
        "iss": JWT_ISS,
        "sub": str(user_id),
        "admin": bool(is_admin),
        "verified_author": bool(is_verified_author),
        "iat": now,
        "exp": now + ACCESS_TTL,
        "type": "access",
        "jti": str(uuid.uuid4()),
    }
    return jwt_encode(payload)

def new_refresh_token(user_id: int) -> tuple[str, str, datetime]:
    now = datetime.now(timezone.utc)
    exp_dt = now + timedelta(seconds=REFRESH_TTL)
    jti = str(uuid.uuid4())
    payload = {
        "iss": JWT_ISS,
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int(exp_dt.timestamp()),
        "type": "refresh",
        "jti": jti,
    }
    return jwt_encode(payload), jti, exp_dt