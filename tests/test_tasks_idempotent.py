import pytest
from sqlalchemy.orm import sessionmaker

from app import models
from app.tasks import send_news_notification, send_weekly_digest


class DummyRedis:
    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def setex(self, key, ttl, value):
        self.store[key] = value

    def set(self, key, value):
        self.store[key] = value


def test_send_news_notification_idempotent(monkeypatch, db_session):
    # 1) redis мок
    r = DummyRedis()
    monkeypatch.setattr("app.tasks.redis_client", r)

    # 2) SessionLocal -> sqlite sessionmaker (ВАЖНО)
    TestSessionLocal = sessionmaker(bind=db_session.get_bind(), autoflush=False, autocommit=False)
    monkeypatch.setattr("app.tasks.SessionLocal", TestSessionLocal)

    # данные
    u1 = models.User(name="u1", email="u1@u", is_admin=False, is_verified_author=False)
    u2 = models.User(name="u2", email="u2@u", is_admin=False, is_verified_author=False)
    db_session.add_all([u1, u2])
    db_session.commit()
    db_session.refresh(u1)
    db_session.refresh(u2)

    n = models.News(title="t", content={"text": "x"}, author_id=u1.id)
    db_session.add(n)
    db_session.commit()
    db_session.refresh(n)

    # ВАЖНО: без None
    send_news_notification(n.id)

    assert r.get(f"notif:news:{n.id}:user:{u1.id}") == "sent"
    assert r.get(f"notif:news:{n.id}:user:{u2.id}") == "sent"

    # повтор — не должен переотправить
    send_news_notification(n.id)
    assert r.get(f"notif:news:{n.id}:user:{u1.id}") == "sent"


def test_send_weekly_digest_idempotent(monkeypatch, db_session):
    r = DummyRedis()
    monkeypatch.setattr("app.tasks.redis_client", r)

    TestSessionLocal = sessionmaker(bind=db_session.get_bind(), autoflush=False, autocommit=False)
    monkeypatch.setattr("app.tasks.SessionLocal", TestSessionLocal)

    u = models.User(name="u", email="u@u", is_admin=False, is_verified_author=False)
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)

    n = models.News(title="digest", content={"text": "y"}, author_id=u.id)
    db_session.add(n)
    db_session.commit()

    send_weekly_digest()
    send_weekly_digest()
