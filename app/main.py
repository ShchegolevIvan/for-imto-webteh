from fastapi import FastAPI
from app.api import router
from app.db import engine, Base
from app import models
app = FastAPI(title="News API")
app.include_router(router)
Base.metadata.create_all(bind=engine)
