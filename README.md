# ЕСИА Gateway FastAPI

Серверное приложение FastAPI для работы с шлюзом ЕСИА (Единая система идентификации и аутентификации).

## Описание

Это полнофункциональное API приложение, которое обеспечивает интеграцию с ЕСИА шлюзом для:
- Авторизации пользователей через ЕСИА
- Получения и обновления токенов доступа
- Получения данных пользователей и организаций
- Управления группами доступа
- Выхода из системы ЕСИА

## Особенности

- **Современная архитектура**: Использует принципы чистой архитектуры с разделением на слои
- **Полная типизация**: TypeHints для всех методов и функций
- **Валидация данных**: Pydantic схемы для валидации входных и выходных данных
- **Обработка ошибок**: Централизованная система обработки исключений
- **Логирование**: Ежедневная ротация логов с разделением по уровням
- **База данных**: MySQL 5.7 с миграциями Alembic
- **Docker**: Готовая конфигурация для развертывания
- **Тестирование**: Полный набор unit тестов
- **Документация**: Автоматическая генерация OpenAPI документации

## Технологический стек

- **Python**: 3.12
- **FastAPI**: Последняя версия
- **SQLAlchemy**: 2.0 (последняя версия)
- **MySQL**: 5.7
- **Alembic**: Миграции базы данных
- **Pydantic**: Валидация данных
- **HTTPX**: HTTP клиент для запросов к ЕСИА
- **Pytest**: Тестирование
- **Docker**: Контейнеризация

## Структура проекта

```
app/
├── api/                    # API роуты
│   └── v1/
│       ├── auth.py        # Авторизация и аутентификация
│       ├── users.py       # Управление пользователями
│       ├── organizations.py # Управление организациями
│       └── router.py      # Главный роутер
├── core/                  # Основные компоненты
│   ├── config.py         # Конфигурация приложения
│   ├── database.py       # Настройка базы данных
│   ├── exceptions.py     # Пользовательские исключения
│   └── logging.py        # Настройка логирования
├── middleware/           # Middleware компоненты
│   ├── cors.py          # CORS middleware
│   └── timing.py        # Request timing middleware
├── models/              # Модели базы данных
│   ├── user.py         # Модели пользователей
│   └── organization.py # Модели организаций
├── repositories/       # Репозитории для работы с данными
│   ├── user.py        # Репозиторий пользователей
│   └── organization.py # Репозиторий организаций
├── schemas/           # Pydantic схемы
│   ├── auth.py       # Схемы авторизации
│   ├── user.py       # Схемы пользователей
│   └── organization.py # Схемы организаций
├── services/         # Бизнес-логика
│   ├── esia.py      # Сервис для работы с ЕСИА
│   ├── user.py      # Сервис пользователей
│   └── organization.py # Сервис организаций
└── main.py          # Главный файл приложения
```

## Установка и запуск

### Локальная разработка

1. **Клонирование репозитория**:
```bash
git clone <repository-url>
cd esia-gateway-fastapi
```

2. **Создание виртуального окружения**:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

3. **Установка зависимостей**:
```bash
pip install -r requirements.txt
```

4. **Настройка переменных окружения**:
```bash
cp .env.example .env
# Отредактируйте .env файл с вашими настройками
```

5. **Запуск миграций**:
```bash
alembic upgrade head
```

6. **Запуск приложения**:
```bash
python -m uvicorn app.main:app --reload
```

### Docker развертывание

1. **Запуск с Docker Compose**:
```bash
docker-compose up -d
```

2. **Запуск миграций в контейнере**:
```bash
docker-compose exec app alembic upgrade head
```

## Конфигурация

Основные настройки приложения задаются через переменные окружения в файле `.env`:

```env
# База данных
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=password
DB_NAME=ESIA_gateway

# ЕСИА настройки
ESIA_DEMO_URL=https://demo.gate.esia.pro
ESIA_CLIENT_ID=your_client_id
ESIA_CLIENT_SECRET=your_client_secret
ESIA_REDIRECT_URI=https://your-domain.com/callback

# Приложение
SECRET_KEY=your-secret-key-here
DEBUG=True
LOG_LEVEL=INFO
```

## API Документация

После запуска приложения документация доступна по адресам:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Основные эндпоинты

### Авторизация
- `GET /api/v1/auth/authorize` - Инициация авторизации
- `POST /api/v1/auth/token` - Получение/обновление токена
- `POST /api/v1/auth/userinfo` - Получение данных пользователя
- `GET /api/v1/auth/logout` - Выход из системы
- `GET /api/v1/auth/callback` - Обработка callback

### Пользователи
- `GET /api/v1/users/` - Список пользователей
- `POST /api/v1/users/` - Создание пользователя
- `GET /api/v1/users/{id}` - Получение пользователя по ID
- `PUT /api/v1/users/{id}` - Обновление пользователя
- `DELETE /api/v1/users/{id}` - Удаление пользователя

### Организации
- `GET /api/v1/organizations/` - Список организаций
- `POST /api/v1/organizations/` - Создание организации
- `GET /api/v1/organizations/{id}` - Получение организации по ID
- `PUT /api/v1/organizations/{id}` - Обновление организации
- `DELETE /api/v1/organizations/{id}` - Удаление организации

## Тестирование

Запуск тестов:
```bash
pytest
```

Запуск тестов с покрытием:
```bash
pytest --cov=app
```

Запуск конкретного теста:
```bash
pytest tests/test_auth.py::TestAuthAPI::test_authorize_endpoint
```

## Логирование

Приложение создает следующие файлы логов в директории `logs/`:
- `app.log` - Общие логи приложения
- `errors.log` - Логи ошибок
- `esia.log` - Логи операций с ЕСИА

Логи ротируются ежедневно с сохранением 30 дней истории.

## База данных

### Структура таблиц

- **users** - Пользователи ЕСИА
- **user_tokens** - Токены пользователей
- **authorization_requests** - Запросы авторизации
- **organizations** - Организации ЕСИА
- **organization_addresses** - Адреса организаций
- **organization_groups** - Группы доступа организаций
- **user_organizations** - Связи пользователей с организациями

### Миграции

Создание новой миграции:
```bash
alembic revision --autogenerate -m "Description"
```

Применение миграций:
```bash
alembic upgrade head
```

Откат миграции:
```bash
alembic downgrade -1
```

## Мониторинг

### Health Check
- `GET /health` - Проверка состояния приложения

### Метрики
- Время выполнения запросов добавляется в заголовок `X-Process-Time`
- Подробное логирование всех операций

## Безопасность

- Валидация всех входных данных через Pydantic
- Централизованная обработка ошибок
- Логирование всех операций
- CORS настройки
- Защита от SQL инъекций через SQLAlchemy ORM

## Разработка

### Добавление новых эндпоинтов

1. Создайте Pydantic схемы в `app/schemas/`
2. Добавьте модели базы данных в `app/models/`
3. Создайте репозиторий в `app/repositories/`
4. Реализуйте бизнес-логику в `app/services/`
5. Добавьте API роуты в `app/api/v1/`
6. Напишите тесты в `tests/`

### Стиль кода

Проект следует принципам:
- Clean Architecture
- SOLID принципы
- Type Hints для всех функций
- Docstrings на русском языке
- Разделение ответственности

## Поддержка

При возникновении проблем:
1. Проверьте логи в директории `logs/`
2. Убедитесь в правильности настроек в `.env`
3. Проверьте доступность базы данных
4. Убедитесь в корректности настроек ЕСИА

## Лицензия

MIT License