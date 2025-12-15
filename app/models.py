from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
    is_verified_author = Column(Boolean, default=False)
    avatar = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    github_id = Column(String, nullable=True, unique=True)
    github_login = Column(String, nullable=True)

class RefreshSession(Base):
    __tablename__ = "refresh_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    token_id = Column(String, nullable=False, index=True)  # jti
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)

    user = relationship("User", backref="refresh_sessions")

Index("ix_refresh_active", RefreshSession.user_id, RefreshSession.revoked)

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(JSON, nullable=False)
    published_at = Column(DateTime(timezone=True), server_default=func.now())
    cover = Column(String, nullable=True)

    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    author = relationship("User", backref="news")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    published_at = Column(DateTime(timezone=True), server_default=func.now())

    news_id = Column(Integer, ForeignKey("news.id", ondelete="CASCADE"))
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    news = relationship("News", backref="comments")
    author = relationship("User", backref="comments")
