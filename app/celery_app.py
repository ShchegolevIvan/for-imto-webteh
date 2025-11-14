# app/celery_app.py
import os
from celery import Celery
from celery.schedules import crontab

REDIS_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
REDIS_BACKEND_URL = os.getenv("CELERY_RESULT_BACKEND", REDIS_BROKER_URL)

celery_app = Celery(
    "news_tasks",
    broker=REDIS_BROKER_URL,
    backend=REDIS_BACKEND_URL,
    include=["app.tasks"],  # важно: чтобы Celery видел таски
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

# Переодический запуск: каждое воскресенье в 12:00 (UTC)
celery_app.conf.beat_schedule = {
    "weekly-digest": {
        "task": "app.tasks.send_weekly_digest",
        "schedule": crontab(hour=12, minute=0, day_of_week="sun"),
    }
}
