# PyTaskHub – Backend MVP

Backend для ToDo приложения | Python + FastAPI + PostgreSQL | MIPT Project

---

## 1. Описание проекта

PyTaskHub - это backend-часть ToDo-приложения, предоставляющая REST API для:

* управления задачами и их статусами
* работы с категориями задач
* регистрации и аутентификации пользователей (JWT)
* работы с профилем пользователя

Проект разрабатывается в учебных целях в рамках курса «Язык Python для разработчиков» и проектного практикума МФТИ.

---

## 2. Технологии

### Backend Framework

* **FastAPI** - асинхронный web-framework
* **Python 3.11+** - язык программирования
* **Uvicorn** - ASGI-сервер

### Database

* **PostgreSQL 15+** - реляционная СУБД
* **SQLAlchemy 2.0** - ORM с асинхронной поддержкой
* **Alembic** - система миграций БД
* **asyncpg** - асинхронный драйвер для PostgreSQL

### Authentication & Security

* **PyJWT** - работа с JSON Web Tokens
* **passlib[bcrypt]** - хеширование паролей
* **python-multipart** - обработка form-data

### Testing

* **pytest** - фреймворк для тестирования
* **pytest-asyncio** - поддержка асинхронных тестов
* **httpx** - асинхронный HTTP-клиент для тестов
* **faker** - генерация тестовых данных

### DevOps

* **Docker** - контейнеризация
* **Docker Compose** - оркестрация контейнеров
* **python-dotenv** - управление переменными окружения

---

## 3. Требования

Для локального запуска проекта необходимы:

* **Python** 3.11 или выше
* **PostgreSQL** 15 или выше
* **Git**
* **Make** (опционально, для использования `Makefile`)
* **Docker** и **Docker Compose** (опционально, для контейнеризированного запуска)

---

## 4. Установка

Все команды ниже выполняются из корневой директории проекта.

### 4.1. Клонирование репозитория

```bash
git clone https://github.com/PyTaskHub/todo-app-backend.git
cd todo-app-backend
```

### 4.2. Создание виртуального окружения

```bash
python3 -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

### 4.3. Установка зависимостей

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 5. Настройка переменных окружения

В репозитории размещён шаблон файла окружения `.env.example` - на его основе следует создать рабочий файл `.env`:

```bash
cp .env.example .env
```

Отредактируйте файл `.env` и установите необходимые значения:

```env
# Application
APP_NAME=PyTaskHub
SECRET_KEY=your-secret-key-here    # Обязательно измените!

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/pytaskhub

# Security
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

Для генерации уникального `SECRET_KEY` можно использовать:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Перед запуском приложения рекомендуется убедиться, что:

* для переменной `SECRET_KEY` сгенерировано и задано уникальное значение (использование значения по умолчанию не допускается)
* корректно настроена переменная `DATABASE_URL`
* указанный порт (по умолчанию `8000`) свободен и не используется другими процессами

---

## 6. Миграции

Перед запуском приложения необходимо применить миграции Alembic, чтобы создать схемы таблиц в базе данных.

### 6.1. Локальный запуск миграций

1. Убедитесь, что PostgreSQL запущен и доступен по адресу из `DATABASE_URL`
2. Выполните команду:

```bash
alembic upgrade head
```

### 6.2. Миграции в Docker

При запуске через Docker:

```bash
# Применить миграции внутри контейнера backend
docker-compose exec backend alembic upgrade head

# Либо через Makefile
make docker-migrate
```

---

## 7. Запуск приложения

Backend-приложение использует PostgreSQL в качестве основной базы данных, поэтому перед запуском сервиса необходимо обеспечить доступность БД.

Возможны два основных сценария:

1. backend запускается локально, а PostgreSQL — локально или в отдельном контейнере
2. backend и PostgreSQL запускаются в контейнерах через `docker-compose`

### 7.1. Запуск PostgreSQL

#### 7.1.1 Через Docker (рекомендуется)

```bash
docker run -d \
  --name pytaskhub-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=pytaskhub \
  -p 5432:5432 \
  postgres:15
```

#### 7.1.2 Локальная установка

- Установите PostgreSQL стандартным способом для используемой ОС и создайте базу данных `pytaskhub`
- Убедитесь, что параметры подключения в `.env` соответствуют фактической конфигурации PostgreSQL

### 7.2. Локальный запуск backend

В этом сценарии backend запускается напрямую на хостовой машине, PostgreSQL - локально или в отдельном контейнере (см. п. 7.1 Запуск PostgreSQL)
	
```bash
# 1. Убедитесь, что PostgreSQL запущен (см. 7.1)

# 2. При первом запуске примените миграции для создания таблиц
alembic upgrade head

# 3. Запустите backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Или через Makefile
make run
````

**Примечание:** Команду `alembic upgrade head` нужно выполнять только:

* При первом запуске проекта (когда база пустая)
* После `git pull`, если в проекте появились новые миграции
* После создания собственных миграций

При обычном перезапуске приложения миграции повторно применять **не нужно**.

### 7.3. Запуск окружения через docker-compose

В этом сценарии backend и PostgreSQL запускаются в Docker-контейнерах.

#### 7.3.1. Быстрый старт
Соберите и запустите контейнеры:

```bash
docker-compose up -d

# или через Makefile
make dev
```

При первом запуске (или после добавления новых миграций) примените миграции внутри контейнера backend:

```bash
docker-compose exec backend alembic upgrade head

# или через Makefile
make docker-migrate
```
#### 7.3.2. Управление Docker-окружением

```bash
# Просмотр логов всех сервисов
docker-compose logs -f
make docker-logs

# Логи только backend
make docker-logs-backend

# Открыть shell в контейнере backend
docker-compose exec backend /bin/sh
make docker-shell

# Остановить контейнеры
docker-compose down
make dev-stop

# Перезапустить контейнеры
docker-compose restart
make dev-restart

# Запустить тесты внутри контейнера backend
docker-compose exec backend pytest
make docker-test
```

---

## 8. Запуск тестов

В активированном виртуальном окружении:

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

Отчёт о покрытии кода будет доступен в `htmlcov/index.html`

---

## 9. API документация

Сервис и документация API доступны по следующим адресам:
* **API**: http://localhost:8000
* **Swagger UI**: http://localhost:8000/api/docs
* **ReDoc**: http://localhost:8000/api/redoc
* **OpenAPI JSON**: http://localhost:8000/api/openapi.json

### Основные endpoints

#### Authentication

- `POST /api/v1/auth/register` - Регистрация нового пользователя
- `POST /api/v1/auth/login` - Аутентификация пользователя
- `POST /api/v1/auth/refresh` - Обновление access токена

#### Users

- `GET /api/v1/users/me` - Получение профиля текущего пользователя
- `PUT /api/v1/users/me` - Обновление профиля
- `POST /api/v1/users/change-password` - Изменение пароля

#### Tasks

- `GET /api/v1/tasks` - Получение списка задач с фильтрацией и пагинацией
- `POST /api/v1/tasks` - Создание новой задачи
- `GET /api/v1/tasks/{id}` - Получение задачи по ID
- `PUT /api/v1/tasks/{id}` - Обновление задачи
- `DELETE /api/v1/tasks/{id}` - Удаление задачи
- `PATCH /api/v1/tasks/{id}/toggle` - Переключение статуса выполнения
- `GET /api/v1/tasks/search` - Поиск задач по названию
- `GET /api/v1/tasks/statistics` - Статистика по задачам

#### Categories

- `GET /api/v1/categories` - Получение списка категорий
- `POST /api/v1/categories` - Создание категории
- `PUT /api/v1/categories/{id}` - Обновление категории
- `DELETE /api/v1/categories/{id}` - Удаление категории

#### System

- `GET /api/health` - Проверка состояния сервиса

---

## 10. Структура проекта

```text
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
│   ├── models/              # SQLAlchemy-модели
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── task.py
│   │   └── category.py
│   ├── schemas/             # Pydantic-схемы
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── task.py
│   │   └── category.py
│   └── crud/                # CRUD-операции
│       ├── __init__.py
│       ├── base.py
│       ├── user.py
│       ├── task.py
│       └── category.py
├── tests/                   # Тесты
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_tasks.py
│   └── test_integration.py
├── alembic/                 # Миграции БД
│   ├── versions/
│   └── env.py
├── docs/                    # Дополнительная документация
├── .env.example             # Шаблон переменных окружения
├── .gitignore
├── requirements.txt         # Python-зависимости
├── alembic.ini              # Конфигурация Alembic
├── Makefile                 # Команды для разработки
└── README.md
```

---

## 11. Команда

* **Артур Юсупов** – Тимлид + Backend Lead
* **Сергей Морозов** – Backend Developer
* **Валерия Махмутова** – Backend Developer
* **Стелла Петрова** – Backend + QA Engineer
* **Алина Патралова** – Backend + Analyst + Junior QA

---

## 12. Troubleshooting

**Проблема:** Контейнеры не запускаются
```bash
docker-compose logs
```
Проверьте:

* корректность `DATABASE_URL` / параметров БД
* доступность БД (контейнер `pytaskhub-db` должен быть в состоянии `healthy`)
* наличие и корректность `.env`

**Проблема:** `ModuleNotFoundError: No module named 'jose'`

При работе через Docker нужно пересобрать образ backend:

```bash
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d
```

**Проблема:** Необходимо сбросить все данные и развернуть окружение заново
```bash
docker-compose down -v
docker-compose up -d
```

**Проблема:** Порт 8000 занят
```env
# Изменить порт в .env
PORT=8001
```
и перезапустить приложение/контейнеры

**Проблема:** Ошибка подключения к базе данных/миграций

Типичные сообщения:

* `asyncpg.exceptions.ConnectionDoesNotExistError`
* `Connection refused` / `could not connect to server`

Проверьте:

1. Запущен ли PostgreSQL (локально или в Docker)
2. Совпадают ли параметры подключения в `.env` с фактическими
3. Применены ли миграции:

```bash
# Локально
alembic upgrade head

# Docker
docker-compose exec backend alembic upgrade head
```

**Проблема:** Приложение не открывается в браузере

* Убедитесь, что сервер запущен (есть логи от `uvicorn` или `docker-compose logs`)
* Проверьте, что обращаетесь по `http://localhost:PORT`, где `PORT` совпадает с `.env`
* В Docker-случае убедитесь, что порт проброшен в `docker-compose.yml`

---

## 13. Workflow разработки

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

---

## 14. Использование Makefile

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

---

## 15. Прогресс проекта

Отслеживание задач и прогресса доступно в [GitHub Projects](https://github.com/orgs/PyTaskHub/projects)

---

## 16. Contribution Guidelines

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

---

## 17. Контакты

**Team Lead**: Артур Юсупов

- GitHub: [@AsyncAssassin](https://github.com/AsyncAssassin)
- Telegram: @aiusupov

---

## 18. Лицензия

Проект распространяется под лицензией MIT License. См. файл LICENSE для подробной информации.

---

## 19. Дополнительная документация

- [SECURITY.md](SECURITY.md) - Рекомендации по безопасности
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Детальное руководство по настройке
- Swagger документация доступна после запуска приложения по адресу `/api/docs`