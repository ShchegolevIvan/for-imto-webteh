from sqlalchemy.orm import Session
from app import models

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

def get_news(db: Session):
    return db.query(models.News).all()

def update_news(db: Session, news_id: int, data: dict):
    news = db.query(models.News).filter(models.News.id == news_id).first()
    if not news:
        return None
    for key, value in data.items():
        setattr(news, key, value)
    db.commit()
    db.refresh(news)
    return news


def delete_news(db: Session, news_id: int):
    news = db.query(models.News).filter(models.News.id == news_id).first()
    if not news:
        return None
    db.delete(news)
    db.commit()
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
