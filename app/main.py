from fastapi import FastAPI, Request
from prometheus_client import make_asgi_app
from starlette.responses import JSONResponse
import structlog

from app.api import router
from app.middleware import RequestLoggingMiddleware
from app.logging_config import setup_logging

setup_logging()
log = structlog.get_logger()

app = FastAPI(title="News API")

app.add_middleware(RequestLoggingMiddleware)

# expose /metrics
app.mount("/metrics", make_asgi_app())

app.include_router(router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log.exception("unhandled_exception", path=request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
