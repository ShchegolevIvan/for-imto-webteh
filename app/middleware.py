import time
import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.metrics import (
    HTTP_REQUESTS_TOTAL,
    HTTP_REQUEST_DURATION_SECONDS,
    USERS_REGISTERED_TOTAL,
    NEWS_CREATED_TOTAL,
)

log = structlog.get_logger()


class RequestLoggingMetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        try:
            response: Response = await call_next(request)
        except Exception:
            duration = time.time() - start

            log.exception(
                "request_failed",
                method=request.method,
                path=request.url.path,
                duration=duration,
            )

            # http-метрики на ошибки
            HTTP_REQUESTS_TOTAL.labels(
                method=request.method,
                path=request.url.path,
                status="500",
            ).inc()
            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=request.method,
                path=request.url.path,
            ).observe(duration)

            raise

        duration = time.time() - start

        # лог на любой ответ (включая 401/403/404)
        log.info(
            "request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration=duration,
        )

        # http-метрики на любой ответ
        HTTP_REQUESTS_TOTAL.labels(
            method=request.method,
            path=request.url.path,
            status=str(response.status_code),
        ).inc()
        HTTP_REQUEST_DURATION_SECONDS.labels(
            method=request.method,
            path=request.url.path,
        ).observe(duration)

        # --- БИЗНЕС-МЕТРИКИ ---
        # считаем попытки создания сущностей (даже если ответ 401/403)
        path = request.url.path
        if request.method == "POST" and path == "/users":
            USERS_REGISTERED_TOTAL.inc()

        if request.method == "POST" and path == "/news":
            NEWS_CREATED_TOTAL.inc()

        return response
