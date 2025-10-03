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

##### **Создать пользователя.**
```
POST /users
```

Пример:
```{
  "name": "example",
  "email": "example@example.com",
  "is_verified_author": true,
  "avatar": "ex.png"
}
```

##### **Получить список всех пользователей.**
```GET /users```

#### Новости

##### **Создать новость** (только для верифицированных авторов).
```POST /news```

Пример:
```
{
  "title": "Первая новость",
  "content": {"text": "first"},
  "author_id": 1,
  "cover": "cover.png"
}
```

>[!def] Если пользователь не верифицирован как автор вернёт 403 Forbidden.

##### **Получить список всех новостей.**
```GET /news```

##### **Обновить новость.**
```PUT /news/{news_id}```

Пример:
`{   "title": "Обновлённый заголовок" }`

##### **Удалить новость.**
```DELETE /news/{news_id}```

#### Комментарии
##### **Создать комментарий к новости.**
```POST /comments```

Пример:
```
{
  "text": "Отличная статья!",
  "news_id": 1,
  "author_id": 2
}
```

##### **Получить список всех комментариев.**
```GET /comments```

##### **Обновить комментарий.**
```PUT /comments/{comment_id}```

Пример:
`{   "text": "Исправленный текст комментария" }`

##### **Удалить комментарий.**
```
DELETE `/comments/{comment_id}`
```

