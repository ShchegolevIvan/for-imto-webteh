import logging
import os
from logging.handlers import RotatingFileHandler

import structlog


def setup_logging() -> None:
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    os.makedirs("logs", exist_ok=True)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level, logging.INFO)
        ),
    )

    root = logging.getLogger()
    root.setLevel(log_level)
    root.handlers.clear()

    console = logging.StreamHandler()
    console.setLevel(log_level)

    file_handler = RotatingFileHandler(
        "logs/app.jsonl",
        maxBytes=10 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)

    root.addHandler(console)
    root.addHandler(file_handler)
