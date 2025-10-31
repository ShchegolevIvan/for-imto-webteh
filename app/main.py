from fastapi import FastAPI
from app.api import router as api_router
from app.api_auth import router as auth_router
from app.api_sso import router as sso_router
from app.db import redis_client
app = FastAPI(title="News API")
app.include_router(auth_router)
app.include_router(sso_router)
app.include_router(api_router)
@app.on_event("startup")
def startup_check():
    try:
        redis_client.ping()
        print("Redis connected")
    except Exception as e:
        print("Redis not available:", e)