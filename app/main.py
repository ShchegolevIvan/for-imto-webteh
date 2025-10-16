from fastapi import FastAPI
from app.api import router as api_router
from app.api_auth import router as auth_router
from app.api_sso import router as sso_router

app = FastAPI(title="News API")
app.include_router(auth_router)
app.include_router(sso_router)
app.include_router(api_router)