# PyTaskHub - Backend MVP

Backend для ToDo приложения | Python + FastAPI + PostgreSQL | MIPT Project

## Команда разработки

- **Артур Юсупов** - Тимлид + Backend Lead
- **Сергей Морозов** - Backend Developer
- **Валерия Махмутова** - Backend Developer
- **Стелла Петрова** - Backend + QA Engineer
- **Алина Патралова** - Backend + Analyst + Junior QA

## Технологический стек

### Backend Framework
- **FastAPI** - асинхронный web framework
- **Python 3.11+** - язык программирования
- **Uvicorn** - ASGI сервер

### Database
- **PostgreSQL 15+** - реляционная СУБД
- **SQLAlchemy 2.0** - ORM с асинхронной поддержкой
- **Alembic** - система миграций БД
- **asyncpg** - асинхронный драйвер для PostgreSQL

### Authentication & Security
- **PyJWT** - реализация JSON Web Tokens
- **passlib[bcrypt]** - хеширование паролей
- **python-multipart** - обработка form data

### Testing
- **pytest** - фреймворк для тестирования
- **pytest-asyncio** - поддержка асинхронных тестов
- **httpx** - асинхронный HTTP клиент для тестов
- **faker** - генерация тестовых данных

### DevOps
- **Docker** - контейнеризация
- **Docker Compose** - оркестрация контейнеров
- **python-dotenv** - управление переменными окружения

## Структура проекта

```
todo-app-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Точка входа FastAPI приложения
│   ├── api/                 # API endpoints
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py       # Агрегация роутеров
│   │       └── endpoints/   # Эндпоинты по функциональности
│   │           ├── __init__.py
│   │           ├── auth.py
│   │           ├── users.py
│   │           ├── tasks.py
│   │           └── categories.py
│   ├── core/                # Ядро приложения
│   │   ├── __init__.py
│   │   ├── config.py        # Конфигурация приложения
│   │   └── security.py      # JWT и хеширование паролей
│   ├── db/                  # Работа с базой данных
│   │   ├── __init__.py
│   │   └── session.py       # Подключение к БД и session management
│   ├── models/              # SQLAlchemy модели
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── task.py
│   │   └── category.py
│   ├── schemas/             # Pydantic схемы для валидации
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── task.py
│   │   └── category.py
│   └── crud/                # CRUD операции
│       ├── __init__.py
│       ├── base.py
│       ├── user.py
│       ├── task.py
│       └── category.py
├── tests/                   # Тестовое покрытие
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_tasks.py
│   └── test_integration.py
├── alembic/                 # Миграции базы данных
│   ├── versions/
│   └── env.py
├── .env.example             # Шаблон переменных окружения
├── .gitignore
├── requirements.txt         # Python зависимости
├── alembic.ini             # Конфигурация Alembic
├── Makefile                # Команды для разработки
└── README.md
```

## Установка и запуск

### Требования

- Python 3.11 или выше
- PostgreSQL 15 или выше
- Docker (опционально)

### 1. Клонирование репозитория

```bash
git clone https://github.com/PyTaskHub/todo-app-backend.git
cd todo-app-backend
```

### 2. Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate  # Windows
```

### 3. Установка зависимостей

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

```bash
cp .env.example .env
```

Отредактируйте файл `.env` и установите необходимые значения:

```env
# Application
APP_NAME=PyTaskHub
SECRET_KEY=your-secret-key-here  # Обязательно измените!

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/pytaskhub

# Security
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

Для генерации SECRET_KEY используйте:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Запуск PostgreSQL

#### Вариант A: Через Docker (рекомендуется)

```bash
docker run -d \
  --name pytaskhub-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=pytaskhub \
  -p 5432:5432 \
  postgres:15
```

#### Вариант B: Локальная установка

Установите PostgreSQL согласно документации для вашей ОС и создайте базу данных `pytaskhub`.

### 6. Применение миграций

```bash
alembic upgrade head
```

### 7. Запуск приложения

```bash
# Режим разработки с auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Или через Makefile
make run
```

Приложение будет доступно по следующим адресам:

- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## Тестирование

### Запуск тестов

```bash
# Все тесты
pytest

# С покрытием кода
pytest --cov=app --cov-report=html --cov-report=term

# Конкретный тест
pytest tests/test_auth.py -v

# Через Makefile
make test
```

Отчет о покрытии будет доступен в `htmlcov/index.html`.

## Docker Deployment

### Быстрый старт с Docker

#### 1. Создать .env файл
```bash
cp .env.example .env
# Отредактируйте SECRET_KEY и другие переменные
```

#### 2. Запустить контейнеры
```bash
# Собрать и запустить
docker-compose up -d

# Или через Makefile
make dev
```

#### 3. Применить миграции
```bash
docker-compose exec backend alembic upgrade head

# Или через Makefile
make docker-migrate
```

#### 4. Доступ к приложению
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Управление Docker
```bash
# Просмотр логов
docker-compose logs -f
make docker-logs

# Логи только backend
make docker-logs-backend

# Открыть shell в контейнере
docker-compose exec backend /bin/sh
make docker-shell

# Остановить контейнеры
docker-compose down
make dev-stop

# Перезапустить
docker-compose restart
make dev-restart

# Запустить тесты в Docker
docker-compose exec backend pytest
make docker-test
```

### Troubleshooting

**Проблема:** Контейнер не запускается
```bash
docker-compose logs
```

**Проблема:** Сбросить все данные
```bash
docker-compose down -v
docker-compose up -d
```

**Проблема:** Порт 8000 занят
```bash
# Изменить порт в .env
PORT=8001
```

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Регистрация нового пользователя
- `POST /api/v1/auth/login` - Аутентификация пользователя
- `POST /api/v1/auth/refresh` - Обновление access токена

### Users

- `GET /api/v1/users/me` - Получение профиля текущего пользователя
- `PUT /api/v1/users/me` - Обновление профиля
- `POST /api/v1/users/change-password` - Изменение пароля

### Tasks

- `GET /api/v1/tasks` - Получение списка задач с фильтрацией и пагинацией
- `POST /api/v1/tasks` - Создание новой задачи
- `GET /api/v1/tasks/{id}` - Получение задачи по ID
- `PUT /api/v1/tasks/{id}` - Обновление задачи
- `DELETE /api/v1/tasks/{id}` - Удаление задачи
- `PATCH /api/v1/tasks/{id}/toggle` - Переключение статуса выполнения
- `GET /api/v1/tasks/search` - Поиск задач по названию
- `GET /api/v1/tasks/statistics` - Статистика по задачам

### Categories

- `GET /api/v1/categories` - Получение списка категорий
- `POST /api/v1/categories` - Создание категории
- `PUT /api/v1/categories/{id}` - Обновление категории
- `DELETE /api/v1/categories/{id}` - Удаление категории

### System

- `GET /api/health` - Проверка состояния сервиса

## Workflow разработки

### Работа с ветками

```bash
# Создание новой ветки
git checkout -b feature/task-{номер}-{описание}

# Пример
git checkout -b feature/task-13-create-task-endpoint
```

### Коммиты

Формат коммитов должен включать номер задачи:

```bash
git add .
git commit -m "#13 Feature: Create Task endpoint"
git push origin feature/task-13-create-task-endpoint
```

### Pull Request Process

1. Создайте Pull Request в GitHub
2. Назначьте reviewer (тимлид: Артур Юсупов)
3. Дождитесь code review и получите approval
4. После одобрения выполните merge в ветку `main`

## Использование Makefile

Проект включает Makefile с часто используемыми командами:

```bash
# Полная настройка проекта (первый запуск)
make setup

# Запуск development сервера
make run

# Запуск тестов
make test

# Форматирование кода
make format

# Проверка стиля кода
make lint

# Создание миграции
make migration message='Description of changes'

# Применение миграций
make migrate

# Управление PostgreSQL
make db-up      # Запуск
make db-down    # Остановка
make db-restart # Перезапуск
```

Полный список команд: `make help`

## Прогресс проекта

Отслеживание задач и прогресса доступно в [GitHub Projects](https://github.com/orgs/PyTaskHub/projects).

## Contribution Guidelines

### Code Style

1. **Форматирование**: Black (line length: 100) + isort
2. **Линтинг**: flake8 (max-line-length: 100)
3. **Type Hints**: Обязательны для всех функций и методов
4. **Docstrings**: Для всех публичных функций, классов и методов
5. **Тестирование**: Минимальное покрытие кода - 80%

### Git Workflow

1. Все коммиты должны быть связаны с номером задачи (например, `#13`)
2. Используйте понятные и описательные названия для коммитов
3. Перед созданием PR убедитесь, что проходят все тесты и линтеры
4. Один PR - одна функция или исправление

### Code Review

- Все Pull Requests требуют одобрения от тимлида
- Отвечайте на комментарии в течение 24 часов
- Исправляйте замечания перед повторным запросом review

## Контакты

**Team Lead**: Артур Юсупов

- GitHub: [@AsyncAssassin](https://github.com/AsyncAssassin)
- Telegram: @aiusupov

## Лицензия

Проект распространяется под лицензией MIT License. См. файл LICENSE для подробной информации.

## Дополнительная документация

- [SECURITY.md](SECURITY.md) - Рекомендации по безопасности
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Детальное руководство по настройке
- Swagger документация доступна после запуска приложения по адресу `/api/docs`