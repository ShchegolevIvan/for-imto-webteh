from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db import get_db
from app import models
from app.security import jwt_decode
from app.db import get_redis
import json, time

def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis)
) -> models.User:
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Auth required")
    token = auth.split(" ", 1)[1]
    try:
        payload = jwt_decode(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token required")
    user_id = int(payload["sub"])
    cache_key = f"user:{user_id}"
    cached = redis_client.get(cache_key)
    if cached:
        data = json.loads(cached)
        user = models.User(**data)
        return user
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    safe_data = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "is_verified_author": user.is_verified_author,
                "is_admin": user.is_admin,
                "avatar": user.avatar,
                "github_id": user.github_id,
                "github_login": user.github_login,
        }
    redis_client.setex(cache_key, 900, json.dumps(safe_data, default=str))
    return user

def require_admin(user: models.User = Depends(get_current_user)) -> models.User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return user

def require_verified_author(user: models.User = Depends(get_current_user)) -> models.User:
    if not (user.is_verified_author or user.is_admin):
        raise HTTPException(status_code=403, detail="Not verified as author")
    return user

def resolve_news(news_id: int, db: Session = Depends(get_db)) -> models.News:
    news = db.query(models.News).filter(models.News.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    return news

def require_owner_news(
    news: models.News = Depends(resolve_news),
    user: models.User = Depends(get_current_user),
) -> models.News:
    if not (user.is_admin or news.author_id == user.id):
        raise HTTPException(status_code=403, detail="Недостаточно прав для этой новости")
    return news

def resolve_comment(comment_id: int, db: Session = Depends(get_db)) -> models.Comment:
    c = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    return c

def require_owner_comment(
    comment: models.Comment = Depends(resolve_comment),
    user: models.User = Depends(get_current_user),
) -> models.Comment:
    if not (user.is_admin or comment.author_id == user.id):
        raise HTTPException(status_code=403, detail="Недостаточно прав для этого комментария")
    return comment
