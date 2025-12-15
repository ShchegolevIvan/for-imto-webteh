from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import redis
import os

DATABASE_URL = "postgresql+psycopg2://ИМЯ_ПОЛЬЗОВАТЕЛЯ:ПАРОЛЬ@localhost:5432/news_db" # введите свой пароль для корректного подключения

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def get_redis():
    return redis_client