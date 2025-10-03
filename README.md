# News API 

Стек: **FastAPI**, **SQLAlchemy**, **Alembic**, **PostgreSQL**.  
Особое правило: публиковать новости могут только пользователи, у которых `is_verified_author = true`.

---
## Запуск проекта

Установить зависимости:
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

---
## Роуты API
#### Пользователи

1. 
```
POST /users
```
**Создать пользователя.**
Пример:
{
  "name": "example",
  "email": "example@example.com",
  "is_verified_author": true,
  "avatar": "ilya.png"
}
2. 
```GET /users```
**Получить список всех пользователей.**

#### Новости
1. 
```POST /news```
**Создать новость** (только для верифицированных авторов).
Пример:
{
  "title": "Первая новость",
  "content": {"text": "first"},
  "author_id": 1,
  "cover": "cover.png"
}
>[!def] Если пользователь не верифицирован как автор вернёт 403 Forbidden.

2. 
```GET /news```
**Получить список всех новостей.**

3.
```PUT /news/{news_id}```
**Обновить новость.**
Пример:
`{   "title": "Обновлённый заголовок" }`
4. 
``DELETE /news/{news_id}```
**Удалить новость.**

#### Комментарии
1. 
```POST /comments```
**Создать комментарий к новости.**
Пример:
{
  "text": "Отличная статья!",
  "news_id": 1,
  "author_id": 2
}
2. 
```GET /comments```
**Получить список всех комментариев.**
3. 
```PUT /comments/{comment_id}```
**Обновить комментарий.**
Пример:
`{   "text": "Исправленный текст комментария" }`

4. 
```
DELETE `/comments/{comment_id}`
```
**Удалить комментарий.**
