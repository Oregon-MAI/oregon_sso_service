# SSO Service

Сервис аутентификации и авторизации. Предоставляет централизованное управление пользователями, ролями и токенами доступа.

## Возможности

- Аутентификация по логину и паролю с хешированием через SHA256
- Выдача пары JWT-токенов: access и refresh
- Ролевая модель: разграничение прав между admin и user
- CRUD-операции над пользователями и ролями с проверкой прав доступа
- Валидация и ротация токенов без повторного ввода пароля
- Экспорт метрик в формате Prometheus
- Распределённая трассировка через OpenTelemetry

## Технологический стек

- Язык: Python 3.14
- Фреймворк: FastAPI
- База данных: PostgreSQL
- ORM: SQLAlchemy 2.0
- Миграции: Alembic
- Аутентификация: JWT
- Логирование: structlog
- Трассировка: OpenTelemetry
- Метрики: Prometheus
- Менеджер зависимостей: uv
- Контейнеризация: Docker

## Быстрый старт

Запуск через Docker Compose:

docker compose up 

Сервис доступен по адрессу http://localhost:8001.

### **Переменные окружения**

- JAEGER: пример: jaeger:4317. Endpoint для экспорта трассировки (gRPC)

## API

Аутентификация:

- POST /api/v1/auth/login: аутентификация пользователя. Тело: login, password. Ответ: профиль с токенами
- POST /api/v1/auth/register: регистрация. Тело: login, password, name, surname, email. Ответ: пара токенов
- POST /api/v1/auth/validate: проверка access-токена. Заголовок: Authorization: Bearer <access_token>. Ответ: is_valid
- POST /api/v1/auth/refresh: обновление токенов. Заголовок: Authorization: Bearer <refresh_token>. Ответ: новая пара токенов

Управление ролями (требует access-токен, операции записи требуют роль admin):

- GET /api/v1/roles/roles: список всех ролей
- GET /api/v1/roles/role?id={uuid}: получение роли по ID
- POST /api/v1/roles/create_role: создание роли
- PATCH /api/v1/roles/update_role: обновление роли
- DELETE /api/v1/roles/delete_role: удаление роли

Управление пользователями (требует access-токен, операции записи требуют роль admin):

- GET /api/v1/user/users: список всех пользователей
- GET /api/v1/user/user?id={uuid}: получение пользователя по ID
- POST /api/v1/user/change_role: назначение роли пользователю
- DELETE /api/v1/user/delete_user: удаление пользователя

Интерактивная документация OpenAPI доступна по адресу http://localhost:8001/docs

## Сценарии использования

Регистрация нового пользователя: пользователь открывает форму регистрации, вводит данные. Клиент отправляет POST /api/v1/auth/register. Сервис проверяет логин, хеширует пароль, создаёт запись с ролью user, генерирует токены и возвращает их.

Вход в систему: пользователь вводит логин и пароль. Клиент отправляет POST /api/v1/auth/login. Сервис проверяет хеш, генерирует новую пару токенов, сохраняет refresh-токен в БД и возвращает профиль.

Доступ к защищённому ресурсу другого сервиса: клиентское приложение делает запрос к стороннему микросервису с заголовком Authorization: Bearer <access_token>. Целевой сервис обращается к POST /api/v1/auth/validate для проверки токена. При успехе сервис извлекает идентификатор и роли, принимает решение о доступе и возвращает данные.

Назначение роли пользователю: администратор выбирает пользователя и роль. Клиент отправляет POST /api/v1/user/change_role с user_id и role_id. Сервис проверяет права администратора, добавляет роль и сохраняет изменения.

## Наблюдаемость

Метрики экспортируются по адресу /metrics в формате Prometheus:

- http_requests_total_manual: общее количество запросов (метки: method, endpoint, status)
- http_errors_total_manual: количество ошибок со статусом 400 и выше
- http_request_duration_seconds_manual: гистограмма времени обработки запроса

Трассировка: каждый запрос получает trace_id, который экспортируется в Jaeger по OTLP gRPC.

Логирование: логи выводятся в JSON-формате в stdout и файл sso.log. Содержат event, level, timestamp, logger, filename, lineno, func_name, trace_id, method, endpoint.

## Структура проекта

```
<pre>
oregon_sso_service/
├── configs/
│ └── prometheus.yml
├── src/
│ ├── alembic.ini
│ ├── constants.py
│ ├── log.py
│ ├── main.py
│ ├── metrics_middleware.py
│ ├── trace.py
│ ├── __init__.py
│ ├── api/
│ │ └── routers/
│ │ ├── auth_router.py
│ │ ├── role_router.py
│ │ └── user_router.py
│ ├── data/
│ │ ├── models/
│ │ │ ├── base.py
│ │ │ ├── role.py
│ │ │ ├── token.py
│ │ │ ├── user.py
│ │ │ └── user_role.py
│ │ ├── repositories/
│ │ │ ├── auth_repository.py
│ │ │ ├── role_repository.py
│ │ │ └── user_repository.py
│ │ └── schemas/
│ │ ├── role.py
│ │ └── user.py
│ ├── migrations/
│ │ ├── env.py
│ │ ├── script.py.mako
│ │ └── versions/
│ └── services/
│ ├── role_service.py
│ ├── security_service.py
│ └── user_service.py
├── tests/
│ ├── conftest.py
│ ├── test_auth_router.py
│ ├── test_repository.py
│ ├── test_role.py
│ ├── test_role_router.py
│ ├── test_security.py
│ ├── test_user_router.py
│ └── test_user_service.py
├── docker-compose.yaml
├── Dockerfile
├── entrypoint.sh
├── pyproject.toml
├── uv.lock
├── .dockerignore
├── .gitignore
├── .python-version
└── README.md
</pre>
```