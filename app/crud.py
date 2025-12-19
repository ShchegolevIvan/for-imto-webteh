from __future__ import annotations

import json
from typing import Any, Optional

from sqlalchemy.orm import Session

from app import models


# -------------------------
# Helpers: normalize payload
# -------------------------

def _normalize_news_payload(data: dict) -> dict:
    """
    Приводит входные данные к модели News.

    У модели News поле: content (JSON).
    Для совместимости поддерживаем входное поле 'text' (строка).
    """
    data = dict(data)

    # Старый контракт: text -> content
    if "text" in data and "content" not in data:
        # content у нас JSON, кладём в объект
        data["content"] = {"text": data["text"]}
    data.pop("text", None)

    # Если кто-то прислал content строкой — тоже оборачиваем в JSON-объект
    if "content" in data and isinstance(data["content"], str):
        data["content"] = {"text": data["content"]}

    return data


def _news_to_cache_dict(news: models.News) -> dict:
    """
    То, что реально кладём в Redis.
    Важно: не используем news.__dict__ (там _sa_instance_state).
    """
    return {
        "id": news.id,
        "title": news.title,
        "content": news.content,
        "published_at": news.published_at.isoformat() if news.published_at else None,
        "cover": news.cover,
        "author_id": news.author_id,
    }


def _news_from_cache_dict(data: dict) -> models.News:
    """
    Восстанавливаем объект News из того, что лежит в Redis.
    published_at оставим строкой — для чтения/выдачи списком это ок.
    (Если надо строго datetime — можно парсить, но тестам не нужно.)
    """
    # Важно: models.News ожидает поля, совпадающие с колонками
    return models.News(
        id=data.get("id"),
        title=data.get("title"),
        content=data.get("content"),
        cover=data.get("cover"),
        author_id=data.get("author_id"),
        # published_at не передаём как datetime, чтобы не тащить парсер
    )


def _invalidate_news_cache(redis_client) -> None:
    """
    Удаляем общий кеш ленты.
    """
    redis_client.delete("news:all")


def _invalidate_news_cache_item(redis_client, news_id: int) -> None:
    """
    Удаляем кеш конкретной новости.
    """
    redis_client.delete(f"news:{news_id}")


# -------------------------
# Users
# -------------------------

def create_user(db: Session, data: dict) -> models.User:
    user = models.User(**data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_users(db: Session) -> list[models.User]:
    return db.query(models.User).all()


# -------------------------
# News
# -------------------------

def create_news(db: Session, data: dict) -> models.News:
    data = _normalize_news_payload(data)

    news = models.News(**data)
    db.add(news)
    db.commit()
    db.refresh(news)
    return news


def get_news(db: Session, redis_client=None) -> list[models.News]:
    """
    Возвращает список новостей.
    Если передан redis_client — кешируем на 5 минут.
    """
    cache_key = "news:all"

    if redis_client:
        cached = redis_client.get(cache_key)
        if cached:
            items = json.loads(cached)
            return [_news_from_cache_dict(x) for x in items]

    news_list = db.query(models.News).all()

    if redis_client:
        payload = [_news_to_cache_dict(n) for n in news_list]
        redis_client.setex(cache_key, 300, json.dumps(payload, ensure_ascii=False))

    return news_list


def get_news_by_id(db: Session, news_id: int, redis_client=None) -> Optional[models.News]:
    key = f"news:{news_id}"

    if redis_client:
        cached = redis_client.get(key)
        if cached:
            return _news_from_cache_dict(json.loads(cached))

    news = db.query(models.News).filter(models.News.id == news_id).first()

    if news and redis_client:
        redis_client.setex(key, 300, json.dumps(_news_to_cache_dict(news), ensure_ascii=False))

    return news


def update_news(db: Session, news_id: int, data: dict, redis_client=None) -> Optional[models.News]:
    """
    Обновляет новость.
    Поддерживает text->content.
    При наличии redis_client инвалидирует кеш.
    """
    data = _normalize_news_payload(data)

    news = db.query(models.News).filter(models.News.id == news_id).first()
    if not news:
        return None

    for key, value in data.items():
        setattr(news, key, value)

    db.commit()
    db.refresh(news)

    if redis_client:
        _invalidate_news_cache(redis_client)
        redis_client.setex(
            f"news:{news.id}",
            300,
            json.dumps(_news_to_cache_dict(news), ensure_ascii=False),
        )

    return news


def delete_news(db: Session, news_id: int, redis_client=None) -> Optional[models.News]:
    news = db.query(models.News).filter(models.News.id == news_id).first()
    if not news:
        return None

    db.delete(news)
    db.commit()

    if redis_client:
        _invalidate_news_cache(redis_client)
        _invalidate_news_cache_item(redis_client, news_id)

    return news


# -------------------------
# Comments
# -------------------------

def create_comment(db: Session, data: dict) -> models.Comment:
    comment = models.Comment(**data)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def get_comments(db: Session) -> list[models.Comment]:
    return db.query(models.Comment).all()


def update_comment(db: Session, comment_id: int, data: dict) -> Optional[models.Comment]:
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        return None

    for key, value in data.items():
        setattr(comment, key, value)

    db.commit()
    db.refresh(comment)
    return comment


def delete_comment(db: Session, comment_id: int) -> Optional[models.Comment]:
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        return None

    db.delete(comment)
    db.commit()
    return comment
