from prometheus_client import Counter, Histogram

# Базовые HTTP метрики
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "path", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
)

# Бизнес-метрики
USERS_REGISTERED_TOTAL = Counter(
    "users_registered_total",
    "Total number of registered users",
)

NEWS_CREATED_TOTAL = Counter(
    "news_created_total",
    "Total number of created news",
)

# Метрика по уведомлениям (из ЛР4/ЛР5)
NOTIFICATIONS_SENT_TOTAL = Counter(
    "notifications_sent_total",
    "Total number of sent notifications",
    ["kind"],  # kind = new_news | weekly_digest
)

