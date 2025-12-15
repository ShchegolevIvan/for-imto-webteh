# app/tasks.py
import logging
from datetime import datetime, timedelta, timezone

from celery import shared_task
from celery.signals import worker_shutdown

from app.db import SessionLocal, redis_client
from app import models
from app.metrics import NOTIFICATIONS_SENT_TOTAL


# ---------- ЛОГИРОВАНИЕ В ФАЙЛ ----------

logger = logging.getLogger("notifications")
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = logging.FileHandler("notifications.log", encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(file_handler)


# ---------- 1) УВЕДОМЛЕНИЯ О НОВОЙ НОВОСТИ ----------

@shared_task(
    bind=True,
    autoretry_for=(Exception,),   # ретраи при ошибках
    retry_backoff=True,           # backoff: 1,2,4,8,...
    retry_jitter=True,
    max_retries=5,
)
def send_news_notification(self, news_id: int):
    """
    Рассылает "моковые" уведомления всем пользователям о новой новости.
    Идемпотентность: per news_id + user_id через Redis-ключ.
    """
    db = SessionLocal()
    try:
        news = db.query(models.News).filter(models.News.id == news_id).first()
        if not news:
            logger.warning(f"[news] news_id={news_id} not found, skip")
            return

        users = db.query(models.User).all()
        key_prefix = f"notif:news:{news_id}"

        for user in users:
            sent_key = f"{key_prefix}:user:{user.id}"

            # идемпотентность — если уже есть ключ, значит уже "отправляли"
            if redis_client.get(sent_key):
                continue

            logger.info(
                f"[news] send NEW_NEWS notification "
                f"to user_id={user.id} email={user.email} "
                f"news_id={news.id} title={news.title!r}"
            )

            # метрика (по ТЗ ЛР7)
            NOTIFICATIONS_SENT_TOTAL.labels(kind="new_news").inc()

            # TTL неделя, чтобы кеш не жил вечно
            redis_client.setex(sent_key, 7 * 24 * 60 * 60, "sent")

    finally:
        db.close()


# ---------- 2) ЕЖЕНЕДЕЛЬНЫЙ ДАЙДЖЕСТ ----------

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=5,
)
def send_weekly_digest(self):
    """
    Раз в неделю отправляет дайджест новостей за последние 7 дней.
    Идемпотентность: digest:<year>-W<week>:user:<id>
    """
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)

        # берем новости за 7 дней
        news_list = (
            db.query(models.News)
            .filter(models.News.published_at >= week_ago)
            .order_by(models.News.published_at.desc())
            .all()
        )

        year, week, _ = now.isocalendar()
        users = db.query(models.User).all()

        for user in users:
            digest_key = f"notif:digest:{year}-W{week}:user:{user.id}"

            # идемпотентность: не отправлять один и тот же дайджест дважды
            if redis_client.get(digest_key):
                continue

            logger.info(
                f"[digest] send WEEKLY_DIGEST to user_id={user.id} email={user.email} "
                f"items={len(news_list)} week={year}-W{week}"
            )

            # дополнительно логируем сами новости (моково)
            for n in news_list:
                logger.info(
                    f"[digest]  -> news_id={n.id} title={n.title!r} "
                    f"published_at={n.published_at}"
                )

            # метрика (по ТЗ ЛР7)
            NOTIFICATIONS_SENT_TOTAL.labels(kind="weekly_digest").inc()

            # помечаем факт отправки дайджеста (на 7 дней)
            redis_client.setex(digest_key, 7 * 24 * 60 * 60, "sent")

    finally:
        db.close()


# ---------- GRACEFUL SHUTDOWN ВОРКЕРА ----------

@worker_shutdown.connect
def on_worker_shutdown(sig, how, exitcode, **kwargs):
    logger.info(f"Celery worker shutting down gracefully: sig={sig}, exitcode={exitcode}")
