Новые поля в User

password_hash — хранение захэшированного пароля (через Argon2).

is_admin — флаг администратора.

github_id, github_login — поддержка авторизации через GitHub.

Новая таблица refresh_sessions
Хранит активные refresh-токены, их jti, user_agent, срок жизни и статус (revoked).

JWT-аутентификация
Реализовано вручную через HMAC-SHA256:

access_token (15 мин) и refresh_token (30 дней).

Ручки /auth/register, /auth/login, /auth/refresh, /auth/logout, /auth/sessions.

OAuth-авторизация через GitHub
Добавлен роут /auth/github/login и /auth/github/callback (через fastapi_sso).

Роль и права доступа

Только админ или владелец может редактировать/удалять новости и комментарии.

Только верифицированные авторы могут публиковать новости.

Зависимости (middleware-подобные проверки)
Вынесена логика проверки прав в app/deps.py:
get_current_user, require_admin, require_verified_author,
require_owner_news, require_owner_comment.

Закрытие всех ручек
Все эндпоинты /users, /news, /comments теперь требуют Authorization: Bearer <token>.

.env-переменные
Добавлены ключи для Postgres, JWT и GitHub OAuth (.env.example).

