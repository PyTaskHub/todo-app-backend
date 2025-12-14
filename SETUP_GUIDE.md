# PyTaskHub - Руководство по настройке проекта

## Задача #1: Setup Project Structure

Это руководство поможет вам настроить проект локально и начать разработку.

---

## Шаг 1: Клонирование приватного репозитория

Репозиторий PyTaskHub/todo-app-backend является приватным. Для клонирования необходим Personal Access Token (PAT).

### 1.1. Создание Personal Access Token

#### Шаг 1.1.1: Открываем настройки GitHub

1. Откройте https://github.com
2. Кликните на свой аватар (правый верхний угол)
3. Выберите **Settings**

#### Шаг 1.1.2: Переходим в Developer settings

1. Прокрутите вниз левое меню
2. Выберите **Developer settings** (самый низ)
3. Выберите **Personal access tokens** → **Tokens (classic)**

#### Шаг 1.1.3: Создаём токен

1. Нажмите **Generate new token** → **Generate new token (classic)**

2. Заполните форму:

```
Note: PyTaskHub Backend Access
Expiration: 90 days
(или No expiration для удобства, но менее безопасно)
```

3. Выберите права доступа (scopes):

```
☑️ repo (выберите ВЕСЬ БЛОК - доступ к приватным репозиториям)
  ☑️ repo:status
  ☑️ repo_deployment
  ☑️ public_repo
  ☑️ repo:invite
  ☑️ security_events

Опционально для работы с организацией:
☑️ admin:org (если вы администратор организации)
☑️ read:org (для чтения информации об организации)
```

4. Нажмите **Generate token** (зелёная кнопка внизу)

#### Шаг 1.1.4: КРИТИЧНО! Сохраните токен

**ВНИМАНИЕ:** Токен показывается только один раз!

Токен выглядит примерно так:
```
ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Действия:**
- Скопируйте токен немедленно
- Сохраните в безопасное место (менеджер паролей, например 1Password, LastPass)
- Или не закрывайте вкладку до завершения клонирования

---

### 1.2. Клонирование через PyCharm (рекомендуется)

#### Вариант A: Через встроенную авторизацию GitHub

1. Откройте PyCharm
2. Выберите **Get from VCS** (или **Clone Repository**)
3. Вставьте URL:
   ```
   https://github.com/PyTaskHub/todo-app-backend.git
   ```
4. Выберите директорию проекта:
   ```
   /Users/ваше_имя/Projects/todo-app-backend
   ```
5. Нажмите **Clone**
6. При запросе авторизации:
   - Выберите **Use token**
   - Вставьте ваш Personal Access Token
   - Нажмите **Log In**

#### Вариант B: Через URL с токеном (если не появляется окно авторизации)

1. Откройте PyCharm
2. Выберите **Get from VCS**
3. Используйте URL с токеном:
   ```
   https://ваш_github_username:ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@github.com/PyTaskHub/todo-app-backend.git
   ```
4. Замените:
   - `ваш_github_username` - на ваш логин GitHub
   - `ghp_xxx...` - на ваш токен
5. Нажмите **Clone**

---

### 1.3. Клонирование через терминал

#### Шаг 1.3.1: Перейдите в директорию проектов

```bash
cd ~/Projects
# или
cd /Users/ваше_имя/Projects
```

#### Шаг 1.3.2: Клонируйте репозиторий

```bash
git clone https://github.com/PyTaskHub/todo-app-backend.git
```

#### Шаг 1.3.3: Введите учетные данные

При запросе аутентификации:

```
Username: ваш_github_username
Password: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**ВАЖНО:** В поле Password вставьте токен, а не ваш пароль GitHub!

#### Альтернативный способ: URL с токеном

```bash
git clone https://ваш_github_username:ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@github.com/PyTaskHub/todo-app-backend.git
```

#### Шаг 1.3.4: Перейдите в директорию проекта

```bash
cd todo-app-backend
```

---

### 1.4. Проверка успешного клонирования

```bash
# Проверьте что файлы скачались
ls -la

# Должны увидеть:
# .env.example
# .gitignore
# README.md
# requirements.txt
# app/
# tests/
# и другие файлы
```

---

## Шаг 2: Создание виртуального окружения

### macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

После активации должно появиться `(venv)` в начале строки терминала.

**Проверка:**
```bash
which python  # macOS/Linux
where python  # Windows

# Должен показать путь внутри venv/
```

---

## Шаг 3: Установка зависимостей

```bash
# Обновляем pip
pip install --upgrade pip

# Устанавливаем зависимости проекта
pip install -r requirements.txt
```

Установка занимает 2-3 минуты.

**Проверка:**
```bash
pip list | grep fastapi
# Должен показать: fastapi 0.115.0 (или новее)
```

---

## Шаг 4: Настройка переменных окружения

### Шаг 4.1: Создайте файл .env

```bash
# Скопируйте шаблон
cp .env.example .env
```

### Шаг 4.2: Сгенерируйте SECRET_KEY

```bash
# Запустите команду для генерации безопасного ключа
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Результат будет похож на:
```
vQx7mK9pL2nR8sT4wY6zB1cD3eF5gH7jKmNpQrStUvWxYz
```

### Шаг 4.3: Отредактируйте .env

Откройте файл `.env` в редакторе:

```bash
# macOS
open .env

# Linux
nano .env

# Windows
notepad .env
```

Измените следующие строки:

```env
# Вставьте сгенерированный ключ
SECRET_KEY=vQx7mK9pL2nR8sT4wY6zB1cD3eF5gH7jKmNpQrStUvWxYz

# Остальные параметры можно оставить по умолчанию для разработки
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/pytaskhub
DEBUG=True
```

**Сохраните файл!**

---

## Шаг 5: Запуск PostgreSQL

### Вариант A: Через Docker (рекомендуется)

```bash
# Используя Makefile
make db-up

# Или вручную
docker run -d \
  --name pytaskhub-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=pytaskhub \
  -p 5432:5432 \
  postgres:15
```

**Проверка:**
```bash
docker ps

# Должен показать:
# CONTAINER ID   IMAGE         ... PORTS                    NAMES
# abc123def456   postgres:15   ... 0.0.0.0:5432->5432/tcp   pytaskhub-db
```

### Вариант B: Локальная установка PostgreSQL

1. Скачайте PostgreSQL с https://www.postgresql.org/download/
2. Установите для вашей ОС
3. Создайте базу данных:

```sql
CREATE DATABASE pytaskhub;
```

4. Убедитесь что PostgreSQL слушает порт 5432

---

## Шаг 6: Запуск приложения

```bash
# Через Makefile (рекомендуется)
make run

# Или напрямую
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Ожидаемый вывод:**
```
INFO:     Will watch for changes in these directories: ['/path/to/todo-app-backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## Шаг 7: Проверка работы приложения

### 7.1. Проверка главной страницы

Откройте в браузере: http://localhost:8000

Должен увидеть JSON ответ:
```json
{
  "message": "Welcome to PyTaskHub!",
  "version": "1.0.0",
  "docs": "/api/docs"
}
```

### 7.2. Проверка Swagger документации

Откройте: http://localhost:8000/api/docs

Должна открыться интерактивная документация API с возможностью тестирования endpoints.

### 7.3. Проверка ReDoc

Откройте: http://localhost:8000/api/redoc

Альтернативное представление API документации.

---

## Шаг 8: Запуск тестов

```bash
# Остановите сервер (Ctrl+C), затем запустите тесты
pytest -v

# Или с покрытием кода
pytest -v --cov=app --cov-report=html --cov-report=term

# Через Makefile
make test
```

**Ожидаемый результат:**
```
tests/test_main.py::test_root_endpoint PASSED               [ 33%]
tests/test_main.py::test_docs_available PASSED              [ 66%]
tests/test_main.py::test_openapi_schema PASSED              [100%]

========== 3 passed in 0.52s ==========
```

---

## Шаг 9: Что дальше?

После успешной настройки:

### 9.1. Создайте рабочую ветку

```bash
# Формат: feature/task-номер-описание
git checkout -b feature/task-X-название

# Примеры:
git checkout -b feature/task-5-user-model
git checkout -b feature/task-13-create-task-endpoint
```

### 9.2. Уведомите команду

Сообщите в Telegram-чат команды что настройка завершена и вы готовы к работе.

### 9.3. Ожидайте назначения задач

Тимлид (Артур) назначит вам задачи согласно плану проекта.

---

## Troubleshooting - Частые проблемы

### Проблема: Authentication failed при клонировании

**Симптом:**
```
remote: Repository not found.
fatal: Authentication failed
```

**Решение:**
1. Убедитесь что используете токен, а не пароль
2. Проверьте что токен имеет права `repo`
3. Убедитесь что вы добавлены в организацию PyTaskHub
4. Попробуйте сгенерировать новый токен

---

### Проблема: ModuleNotFoundError: No module named 'fastapi'

**Симптом:**
```python
ModuleNotFoundError: No module named 'fastapi'
```

**Решение:**
```bash
# Проверьте что venv активирован
which python  # Должен показать путь в venv/

# Если нет - активируйте
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Переустановите зависимости
pip install -r requirements.txt
```

---

### Проблема: could not connect to server: Connection refused

**Симптом:**
```
sqlalchemy.exc.OperationalError: could not connect to server: Connection refused
```

**Решение:**
```bash
# Проверьте что PostgreSQL запущен
docker ps | grep pytaskhub-db

# Если не запущен
make db-up

# Проверьте логи
docker logs pytaskhub-db
```

---

### Проблема: Address already in use (порт 8000 занят)

**Симптом:**
```
OSError: [Errno 48] Address already in use
```

**Решение:**

**macOS/Linux:**
```bash
# Найдите процесс на порту 8000
lsof -ti:8000

# Убейте процесс
lsof -ti:8000 | xargs kill -9
```

**Windows:**
```bash
# Найдите процесс
netstat -ano | findstr :8000

# Убейте процесс (замените PID на фактический номер)
taskkill /PID <номер_процесса> /F
```

---

### Проблема: Тесты падают с ошибкой

**Симптом:**
Тесты не проходят или выдают ошибки.

**Решение:**
1. Убедитесь что приложение НЕ запущено (остановите uvicorn)
2. Очистите кеш:
   ```bash
   make clean
   ```
3. Переустановите зависимости:
   ```bash
   pip install --force-reinstall -r requirements.txt
   ```
4. Запустите тесты снова:
   ```bash
   pytest -v
   ```

---

### Проблема: Permission denied при клонировании

**Симптом:**
```
Permission denied (publickey)
```

**Решение:**
Используйте HTTPS клонирование с токеном вместо SSH:
```bash
# Вместо git@github.com:PyTaskHub/...
# Используйте https://
git clone https://USERNAME:TOKEN@github.com/PyTaskHub/todo-app-backend.git
```

---

## Контакты для помощи

**Тимлид:** Артур Юсупов
- GitHub: [@AsyncAssassin](https://github.com/AsyncAssassin)
- Telegram: @aiusupov
- Время доступности: 08:00-22:00

**Общий чат команды:** [Telegram группа PyTaskHub]

---

## Чеклист готовности к разработке

Отметьте все пункты перед началом работы:

- [ ] Создан и сохранен Personal Access Token
- [ ] Репозиторий успешно склонирован
- [ ] Виртуальное окружение создано и активировано
- [ ] Все зависимости установлены (проверка: `pip list`)
- [ ] Файл .env создан и настроен
- [ ] SECRET_KEY сгенерирован и установлен
- [ ] PostgreSQL запущен и доступен
- [ ] Приложение запускается без ошибок
- [ ] Swagger docs доступна по http://localhost:8000/api/docs
- [ ] Все 3 базовых теста проходят успешно
- [ ] Создана рабочая ветка для разработки

**Когда все пункты выполнены - вы готовы к разработке!**

---

## Дополнительные ресурсы

- [README.md](README.md) - Основная документация проекта
- [SECURITY.md](SECURITY.md) - Рекомендации по безопасности
- [GitHub Projects](https://github.com/orgs/PyTaskHub/projects) - Отслеживание задач
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Официальная документация FastAPI
