import time
import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.metrics import HTTP_REQUESTS_TOTAL, HTTP_REQUEST_DURATION_SECONDS

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
            # метрики на ошибки тоже считаем как 500 (прометей всё равно увидит)
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

        log.info(
            "request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration=duration,
        )

        HTTP_REQUESTS_TOTAL.labels(
            method=request.method,
            path=request.url.path,
            status=str(response.status_code),
        ).inc()

        HTTP_REQUEST_DURATION_SECONDS.labels(
            method=request.method,
            path=request.url.path,
        ).observe(duration)

        return response
