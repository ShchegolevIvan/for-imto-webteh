from sqlalchemy.orm import Session
from app import models
import json, time

def create_user(db: Session, data: dict):
    user = models.User(**data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_users(db: Session):
    return db.query(models.User).all()

def create_news(db: Session, data: dict):
    news = models.News(**data)
    db.add(news)
    db.commit()
    db.refresh(news)
    return news

def get_news(db: Session, redis_client=None):
    """Возвращает список новостей с кэшем (TTL 5 минут)"""
    cache_key = "news:all"
    if redis_client:
        cached = redis_client.get(cache_key)
        if cached:
            return [models.News(**n) for n in json.loads(cached)]

    news = db.query(models.News).all()
    if redis_client:
        redis_client.setex(cache_key, 300, json.dumps([n.__dict__ for n in news], default=str))
    return news


def get_news_by_id(db: Session, news_id: int, redis_client=None):
    key = f"news:{news_id}"
    if redis_client:
        cached = redis_client.get(key)
        if cached:
            return models.News(**json.loads(cached))
    news = db.query(models.News).filter(models.News.id == news_id).first()
    if news and redis_client:
        redis_client.setex(key, 300, json.dumps(news.__dict__, default=str))
    return news

def update_news(db: Session, news_id: int, data: dict):
    news = db.query(models.News).filter(models.News.id == news_id).first()
    if not news:
        return None
    for key, value in data.items():
        setattr(news, key, value)
    db.commit()
    db.refresh(news)
    if news:
        from app.db import redis_client
        redis_client.delete("news:all")
        redis_client.setex(f"news:{news.id}", 300, json.dumps(news.__dict__, default=str))
    return news


def delete_news(db: Session, news_id: int):
    news = db.query(models.News).filter(models.News.id == news_id).first()
    if not news:
        return None
    db.delete(news)
    db.commit()
    from app.db import redis_client
    redis_client.delete("news:all")
    redis_client.delete(f"news:{news_id}")
    return news

def create_comment(db: Session, data: dict):
    comment = models.Comment(**data)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

def get_comments(db: Session):
    return db.query(models.Comment).all()


def update_comment(db: Session, comment_id: int, data: dict):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        return None
    for key, value in data.items():
        setattr(comment, key, value)
    db.commit()
    db.refresh(comment)
    return comment

def delete_comment(db: Session, comment_id: int):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        return None
    db.delete(comment)
    db.commit()
    return comment
