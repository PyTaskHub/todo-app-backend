# Руководство пользователя API

Подробное руководство по использованию API сервиса задач.  
Содержит примеры `curl`, Python-клиента, типовые сценарии, FAQ и подсказки по отладке.

---

## 1. Общая информация

### Базовый URL

По умолчанию (локальный запуск):

```text
http://localhost:8000
````

Основные префиксы:

* Аутентификация: `/api/v1/auth`
* Задачи: `/api/v1/tasks`
* Категории: `/api/v1/categories`
* Пользователь: `/api/v1/users`
* System: `/health`

Во всех примерах ниже для краткости используется `localhost:8000`.
При развёртывании замените на реальный домен/порт.

### Формат запросов

* Тело запросов: **JSON**
* Ответы: **JSON**
* Защищённые эндпоинты требуют заголовок:

```http
Authorization: Bearer <access_token>
```

---

## 2. Health-check

### 2.1 Проверка состояния приложения и БД

**Эндпоинт**

```http
GET /health
```

**Описание**

* Проверяет доступность базы данных
* Возвращает:

  * статус приложения (`healthy` / `unhealthy`)
  * статус БД (`connected` / `unavailable`)
  * актуальный UTC timestamp

**Пример `curl`**

```bash
curl -X GET http://localhost:8000/health
```

**Пример ответа (200 OK)**

```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-11-25T10:00:00Z"
}
```

---

## 3. Аутентификация

Префикс:

```text
/api/v1/auth
```

Модели:

* `UserCreate`
* `UserLogin`
* `Token`
* `RefreshTokenRequest`
* `AccessTokenResponse`

### 3.1 Регистрация пользователя

**Эндпоинт**

```http
POST /api/v1/auth/register
```

**Тело запроса (`UserCreate`)**

```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "MySecurePass123!"
}
```

Требования:

* `username` - 3-50 символов, уникален
* `email` - валидный и уникальный
* `password` - 8-100 символов

**Пример `curl`**

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "MySecurePass123!"
      }'
```

**Пример Python (`requests`)**

```python
import requests

url = "http://localhost:8000/api/v1/auth/register"
data = {
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "MySecurePass123!"
}
r = requests.post(url, json=data)
print(r.status_code, r.json())
```

**Успешный ответ (`UserResponse`, 201 Created)**

```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-11-25T10:00:00Z",
  "updated_at": "2025-11-25T10:00:00Z"
}
```

**Возможные ошибки**

* `409 Conflict` - email или username уже заняты:

  * `{"detail": "Email already registered"}`
  * `{"detail": "Username already taken"}`
* `422 Unprocessable Entity` - ошибка валидации тела запроса

---

### 3.2 Логин

**Эндпоинт**

```http
POST /api/v1/auth/login
```

**Тело запроса (`UserLogin`)**

```json
{
  "email": "john@example.com",
  "password": "MySecurePass123!"
}
```

**Пример `curl`**

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
        "email": "john@example.com",
        "password": "MySecurePass123!"
      }'
```

**Пример Python**

```python
import requests

url = "http://localhost:8000/api/v1/auth/login"
data = {
    "email": "john@example.com",
    "password": "MySecurePass123!"
}
r = requests.post(url, json=data)
tokens = r.json()
access_token = tokens["access_token"]
refresh_token = tokens["refresh_token"]
print(tokens)
```

**Успешный ответ (`Token`, 200 OK)**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.access...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.refresh...",
  "token_type": "bearer"
}
```

**Возможные ошибки**

* `401 Unauthorized`:

  * `{"detail": "Incorrect email or password"}`
  * `{"detail": "Inactive user"}`

---

### 3.3 Обновление access-токена

**Эндпоинт**

```http
POST /api/v1/auth/refresh
```

**Тело запроса (`RefreshTokenRequest`)**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.refresh..."
}
```

**Пример `curl`**

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.refresh..."
      }'
```

**Пример Python**

```python
import requests

url = "http://localhost:8000/api/v1/auth/refresh"
data = {"refresh_token": refresh_token}
r = requests.post(url, json=data)
print(r.status_code, r.json())
```

**Успешный ответ (`AccessTokenResponse`, 200 OK)**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.access...",
  "token_type": "bearer"
}
```

**Возможные ошибки (401 Unauthorized)**

* `{"detail": "Invalid refresh token"}`
* `{"detail": "Invalid token type"}`
* `{"detail": "Invalid token payload"}`
* `{"detail": "User not found"}`
* `{"detail": "Inactive user"}`

---

## 4. Модель пользователя и профиль

Префикс:

```text
/api/v1/users
```

### Основные схемы

* `UserResponse` - профиль пользователя в ответах
* `UserProfileUpdate` - обновление профиля
* `ChangePassword` - смена пароля

---

### 4.1 Получить текущего пользователя

**Эндпоинт**

```http
GET /api/v1/users/me
```

**Требуется**

* Заголовок `Authorization: Bearer <access_token>`

**Пример `curl`**

```bash
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer <access_token>"
```

**Пример ответа (`UserResponse`)**

```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-11-25T10:00:00Z",
  "updated_at": "2025-11-25T10:00:00Z"
}
```

**Возможные ошибки**

* `401 Unauthorized` - нет/невалидный токен

---

### 4.2 Обновить профиль текущего пользователя

**Эндпоинт**

```http
PUT /api/v1/users/me
```

**Тело запроса (`UserProfileUpdate`)**

Все поля опциональны:

```json
{
  "email": "new.email@example.com",
  "first_name": "Johnny",
  "last_name": "Doe"
}
```

**Пример `curl`**

```bash
curl -X PUT http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
        "email": "new.email@example.com",
        "first_name": "Johnny"
      }'
```

**Возможные ошибки**

* `401 Unauthorized` - нет/невалидный токен
* `409 Conflict` - `{"detail": "Email already registered"}`

---

### 4.3 Смена пароля

**Эндпоинт**

```http
POST /api/v1/users/me/change-password
```

**Тело запроса (`ChangePassword`)**

```json
{
  "current_password": "MyCurrentPass123!",
  "new_password": "MyNewSecurePass456!"
}
```

**Пример `curl`**

```bash
curl -X POST http://localhost:8000/api/v1/users/me/change-password \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
        "current_password": "MyCurrentPass123!",
        "new_password": "MyNewSecurePass456!"
      }'
```

**Успешный ответ (200 OK)**

```json
{
  "message": "Password changed successfully"
}
```

**Возможные ошибки**

* `401 Unauthorized` - неверный текущий пароль:
  * `{"detail": "Incorrect current password"}`
* `422 Unprocessable Entity` - валидация (слишком короткий новый пароль и т.п.)

---

## 5. Задачи (Tasks)

Префикс:

```text
/api/v1/tasks
```

Основные схемы:

* `TaskCreate`, `TaskUpdate`
* `TaskResponse`
* `TaskListResponse`
* `TaskStatsResponse`
* фильтры: `TaskSortBy`, `SortOrder`, `StatusFilter`

### 5.1 Структура задачи (`TaskResponse`)

Пример ответа:

```json
{
  "id": 10,
  "title": "Buy groceries",
  "description": "Buy milk, eggs and bread",
  "category_id": 1,
  "priority": "medium",
  "due_date": "2025-12-31T18:00:00Z",
  "user_id": 1,
  "status": "pending",
  "created_at": "2025-11-25T10:00:00Z",
  "updated_at": "2025-11-25T10:00:00Z",
  "completed_at": null,
  "category_name": "Home",
  "category_description": "Home-related tasks"
}
```

---

### 5.2 Создать новую задачу

**Эндпоинт**

```http
POST /api/v1/tasks/
```

**Тело запроса (`TaskCreate`)**

```json
{
  "title": "Buy groceries",
  "description": "Buy milk, eggs, tea, coffee",
  "category_id": 1,
  "priority": "high",
  "due_date": "2025-12-31T18:00:00Z"
}
```

**Пример `curl`**

```bash
curl -X POST http://localhost:8000/api/v1/tasks/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
        "title": "Buy groceries",
        "description": "Buy milk, eggs, tea, coffee",
        "category_id": 1,
        "priority": "high",
        "due_date": "2025-12-31T18:00:00Z"
      }'
```

Ответ - `TaskResponse`

---

### 5.3 Обновить существующую задачу

**Эндпоинт**

```http
PUT /api/v1/tasks/{task_id}
```

**Тело запроса (`TaskUpdate`)** — все поля опциональны:

```json
{
  "title": "Buy oat milk",
  "description": "Replace cow milk with oat milk",
  "priority": "medium",
  "category_id": 2,
  "due_date": "2026-01-10T12:00:00Z"
}
```

**Пример `curl`**

```bash
curl -X PUT http://localhost:8000/api/v1/tasks/10 \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
        "priority": "low"
      }'
```

Ответ - `TaskResponse`

---

### 5.4 Получить одну задачу

**Эндпоинт**

```http
GET /api/v1/tasks/{task_id}
```

**Пример `curl`**

```bash
curl -X GET http://localhost:8000/api/v1/tasks/10 \
  -H "Authorization: Bearer <access_token>"
```

Ответ - `TaskResponse`

---

### 5.5 Получить список задач с фильтрацией и пагинацией

**Эндпоинт**

```http
GET /api/v1/tasks/
```

**Параметры query**

* `limit` (int, 1-100, по умолчанию 20) - размер страницы
* `offset` (int, ≥0, по умолчанию 0) - смещение
* `status_filter` (`all` / `pending` / `completed`, по умолчанию `all`)
* `search` (str, опционально) - поиск по `title` (case-insensitive)
* `category_id` (str):

  * `"{id}"` - задачи этой категории
  * `null` - задачи без категории
  * не передавать - все задачи
* `sort_by` (`created_at` / `priority` / `due_date` / `status`, по умолчанию `created_at`)
* `order` (`asc` / `desc`, по умолчанию `desc`)

**Пример `curl`**

```bash
curl -X GET "http://localhost:8000/api/v1/tasks/?limit=20&offset=0&status_filter=pending&sort_by=due_date&order=asc" \
  -H "Authorization: Bearer <access_token>"
```

**Пример ответа (`TaskListResponse`)**

```json
{
  "items": [
    {
      "id": 10,
      "title": "Buy groceries",
      "description": "Buy milk, eggs and bread",
      "category_id": 1,
      "priority": "medium",
      "due_date": "2025-12-31T18:00:00Z",
      "user_id": 1,
      "status": "pending",
      "created_at": "2025-11-25T10:00:00Z",
      "updated_at": "2025-11-25T10:00:00Z",
      "completed_at": null,
      "category_name": "Home",
      "category_description": "Home-related tasks"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

---

### 5.6 Удалить задачу

**Эндпоинт**

```http
DELETE /api/v1/tasks/{task_id}
```

**Пример `curl`**

```bash
curl -X DELETE http://localhost:8000/api/v1/tasks/10 \
  -H "Authorization: Bearer <access_token>"
```

Ответ: `204 No Content` при успехе

---

### 5.7 Пометить задачу выполненной

**Эндпоинт**

```http
PATCH /api/v1/tasks/{task_id}/complete
```

**Пример `curl`**

```bash
curl -X PATCH http://localhost:8000/api/v1/tasks/10/complete \
  -H "Authorization: Bearer <access_token>"
```

* `status` → `"completed"`
* `completed_at` заполняется текущим временем

---

### 5.8 Вернуть задачу в статус "pending"

**Эндпоинт**

```http
PATCH /api/v1/tasks/{task_id}/uncomplete
```

**Пример `curl`**

```bash
curl -X PATCH http://localhost:8000/api/v1/tasks/10/uncomplete \
  -H "Authorization: Bearer <access_token>"
```

* `status` → `"pending"`
* `completed_at` → `null`

---

### 5.9 Статистика по задачам

**Эндпоинт**

```http
GET /api/v1/tasks/stats
```

**Пример `curl`**

```bash
curl -X GET http://localhost:8000/api/v1/tasks/stats \
  -H "Authorization: Bearer <access_token>"
```

**Пример ответа (`TaskStatsResponse`)**

```json
{
  "total": 25,
  "completed": 15,
  "pending": 10,
  "completion_rate": 60.0
}
```

---

## 6. Категории

Префикс:

```text
/api/v1/categories
```

Схемы:

* `CategoryCreate`
* `CategoryUpdate`
* `CategoryResponse`
* `CategoryListItem`

### 6.1 Создать категорию

**Эндпоинт**

```http
POST /api/v1/categories/
```

**Тело запроса (`CategoryCreate`)**

```json
{
  "name": "Work",
  "description": "Tasks related to work"
}
```

**Пример `curl`**

```bash
curl -X POST http://localhost:8000/api/v1/categories/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
        "name": "Work",
        "description": "Tasks related to work"
      }'
```

**Пример ответа (`CategoryResponse`)**

```json
{
  "id": 1,
  "name": "Work",
  "description": "Tasks related to work",
  "user_id": 1,
  "created_at": "2025-11-25T10:00:00Z",
  "updated_at": "2025-11-25T10:05:00Z"
}
```

---

### 6.2 Обновить категорию

**Эндпоинт**

```http
PUT /api/v1/categories/{category_id}
```

**Тело запроса (`CategoryUpdate`)**

Все поля опциональны:

```json
{
  "name": "Personal",
  "description": "Personal tasks"
}
```

**Пример `curl`**

```bash
curl -X PUT http://localhost:8000/api/v1/categories/1 \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
        "name": "Personal"
      }'
```

**Возможные ошибки**

* `404 Not Found` - категория не найдена или не принадлежит пользователю
* `409 Conflict` - категория с таким `name` уже есть у этого пользователя

---

### 6.3 Получить список категорий пользователя

**Эндпоинт**

```http
GET /api/v1/categories/
```

Возвращает список `CategoryListItem`:

```json
[
  {
    "id": 1,
    "name": "Work",
    "description": "Work-related tasks",
    "tasks_count": 3,
    "created_at": "2025-11-25T10:00:00Z"
  },
  {
    "id": 2,
    "name": "Personal",
    "description": "Personal todos",
    "tasks_count": 5,
    "created_at": "2025-11-26T09:30:00Z"
  }
]
```

**Пример `curl`**

```bash
curl -X GET http://localhost:8000/api/v1/categories/ \
  -H "Authorization: Bearer <access_token>"
```

---

### 6.4 Удалить категорию

**Эндпоинт**

```http
DELETE /api/v1/categories/{category_id}
```

Особенности:

* Только владелец может удалить категорию
* Все задачи с этой категорией становятся "без категории" (`category_id = null`)

**Пример `curl`**

```bash
curl -X DELETE http://localhost:8000/api/v1/categories/1 \
  -H "Authorization: Bearer <access_token>"
```

Ответ: `204 No Content` при успехе

---

## 7. Типовые сценарии

### 7.1 Первый запуск: регистрация → логин → создание задачи

1. **Регистрация**

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
        "username": "john_doe",
        "email": "john@example.com",
        "password": "MySecurePass123!"
      }'
```

2. **Логин**

```bash
TOKENS=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
        "email": "john@example.com",
        "password": "MySecurePass123!"
      }')

ACCESS_TOKEN=$(echo "$TOKENS" | jq -r '.access_token')
```

3. **Создать задачу**

```bash
curl -X POST http://localhost:8000/api/v1/tasks/ \
  -H "Authorization: Bearer '"$ACCESS_TOKEN"'" \
  -H "Content-Type: application/json" \
  -d '{
        "title": "My first task",
        "priority": "medium"
      }'
```

---

### 7.2 Категории и задачи

1. Создать категорию:

```bash
curl -X POST http://localhost:8000/api/v1/categories/ \
  -H "Authorization: Bearer '"$ACCESS_TOKEN"'" \
  -H "Content-Type: application/json" \
  -d '{
        "name": "Home",
        "description": "Home-related tasks"
      }'
```

2. Создать задачу в категории `id=1`:

```bash
curl -X POST http://localhost:8000/api/v1/tasks/ \
  -H "Authorization: Bearer '"$ACCESS_TOKEN"'" \
  -H "Content-Type: application/json" \
  -d '{
        "title": "Clean kitchen",
        "category_id": 1
      }'
```

---

### 7.3 Поиск и сортировка задач

```bash
curl -X GET "http://localhost:8000/api/v1/tasks/?search=report&status_filter=pending&sort_by=priority&order=desc" \
  -H "Authorization: Bearer '"$ACCESS_TOKEN"'"
```

---

### 7.4 Обновление и завершение задачи

```bash
# обновить приоритет
curl -X PUT http://localhost:8000/api/v1/tasks/10 \
  -H "Authorization: Bearer '"$ACCESS_TOKEN"'" \
  -H "Content-Type: application/json" \
  -d '{"priority": "high"}'

# пометить выполненной
curl -X PATCH http://localhost:8000/api/v1/tasks/10/complete \
  -H "Authorization: Bearer '"$ACCESS_TOKEN"'"
```

---

### 7.5 Получить статистику задач

```bash
curl -X GET http://localhost:8000/api/v1/tasks/stats \
  -H "Authorization: Bearer '"$ACCESS_TOKEN"'"
```

---

## 8. Ошибки и отладка

### 8.1 Частые HTTP-коды

* `400 Bad Request` - некорректные данные (обычно подробнее в `detail`)
* `401 Unauthorized` - нет токена / неверные креды / истёк токен
* `403 Forbidden` - попытка доступа к чужим ресурсам (в слоях, где это проверяется)
* `404 Not Found` - ресурс не найден или не принадлежит пользователю
* `409 Conflict` - конфликт уникальности (`email`, `username`, `category name`)
* `422 Unprocessable Entity` - ошибка валидации (неверный формат/типы полей)

### 8.2 Типичные проблемы

**Проблема:** всегда получаю `401 Incorrect email or password`
**Проверить:**

* правильность `email` и `password`
* существует ли пользователь, зарегистрирован ли он через `/auth/register`

---

**Проблема:** `401 Invalid refresh token` / `Invalid token type`
**Проверить:**

* не перепутан ли `access_token` и `refresh_token`
* не истёк ли refresh-токен
* корректно ли передан в теле запроса

---

**Проблема:** `409 Email already registered` при обновлении профиля
**Проверить:**

* нет ли другого пользователя с этим email

---

### 8.3 Чек-лист отладки

1. Правильный ли URL и HTTP-метод?
2. Отправляете ли `Content-Type: application/json` там, где нужен JSON?
3. Является ли тело запроса валидным JSON?
4. Есть ли заголовок `Authorization: Bearer <access_token>`?
5. Не истек ли токен? Попробуйте обновить через `/auth/refresh`

---

## 9. FAQ

### Чем отличаются access и refresh токены?

* **access_token** - используется в заголовке `Authorization` для доступа к защищенным эндпоинтам, живет недолго
* **refresh_token** - только для получения нового access-токена через `/auth/refresh`

---

### Можно ли использовать refresh-токен в `Authorization`?

Нет. Для заголовка `Authorization: Bearer ...` нужно использовать **access_token**
Refresh-токен передается в теле запроса на `/auth/refresh`

---

### Как получить список всех моих задач?

Вызвать:

```http
GET /api/v1/tasks/
```

с заголовком `Authorization: Bearer <access_token>`

---

### Как быстро проверить, что сервис "живой"?

Вызвать health-check:

```bash
curl http://localhost:8000/health
```

Если все в порядке: `status: "healthy"` и `database: "connected"`

---

### Что происходит с задачами при удалении категории?

При удалении категории:

* категория удаляется
* задачи, привязанные к ней, остаются, но их `category_id` становится `null`

---

### Можно ли создать две категории с одинаковым названием?

Для одного и того же пользователя - нет
При попытке создать категорию с уже существующим именем придёт ошибка `409 Conflict`, например:

```json
{
  "detail": "Category with this name already exists"
}
```