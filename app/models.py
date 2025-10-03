from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
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
