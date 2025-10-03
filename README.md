# News API 

Стек: **FastAPI**, **SQLAlchemy**, **Alembic**, **PostgreSQL**.  
Особое правило: публиковать новости могут только пользователи, у которых `is_verified_author = true`.

---

## Запуск проекта

1. Установить зависимости:
   ```
   pip install -r requirements.txt
   ```
Настроить подключение к базе в app/db.py:
```
DATABASE_URL = "postgresql+psycopg2://postgres:password@localhost:5432/news_db"
```
Создать базу данных:
```
sudo -u postgres psql -c "CREATE DATABASE news_db;"
```
Применить миграции:
```
alembic upgrade head
```
Запустить сервер:
```
uvicorn app.main:app --reload
```
API будет доступно по адресу: http://127.0.0.1:8000
Документация Swagger: http://127.0.0.1:8000/docs
---
## Роуты API
## Пользователи
POST /users
Создать пользователя.
Пример:
{
  "name": "example",
  "email": "example@example.com",
  "is_verified_author": true,
  "avatar": "ilya.png"
}
GET /users
Получить список всех пользователей.

Новости
POST /news
Создать новость (только для верифицированных авторов).
Пример:
{
  "title": "Первая новость",
  "content": {"text": "Привет FastAPI"},
  "author_id": 1,
  "cover": "cover.png"
}
Если пользователь не верифицирован как автор → вернёт 403 Forbidden.
GET /news
Получить список всех новостей.
Комментарии
POST /comments
Создать комментарий к новости.
Пример:
{
  "text": "Отличная статья!",
  "news_id": 1,
  "author_id": 2
}
GET /comments
Получить список всех комментариев.
