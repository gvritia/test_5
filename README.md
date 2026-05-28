# Контрольная работа №5

FastAPI-приложение для задач, пользователей, админских операций и WebSocket-комнат.

## Локальный запуск

```bash
python -m venv .venv
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Тесты

```bash
pytest
```

## Docker

```bash
docker compose up --build
```

Проверка:

```bash
curl http://localhost:8000/tasks -H "X-User-Id: 10"
```

Для пустого списка задач ответ будет:

```json
[]
```

## Авторизация

Для имитации пользователя используются заголовки:

```http
X-User-Id: 10
X-User-Role: user
```

`X-User-Role` необязателен и по умолчанию равен `user`. Для админских маршрутов нужен `X-User-Role: admin`.

## Пример POST-запроса

Важные данные передаются через JSON-тело запроса, а не через параметры строки:

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -H "X-User-Id: 10" \
  -d '{"title":"Подготовить тесты","description":"Написать интеграционные тесты","status":"todo","priority":4}'
```

## HTTP-эндпоинты и статусы

| Метод | Маршрут | Возможные статусы |
| --- | --- | --- |
| GET | `/health` | 200 |
| POST | `/tasks` | 201, 400, 401, 422 |
| GET | `/tasks` | 200, 401, 422 |
| GET | `/tasks/{task_id}` | 200, 401, 404, 422 |
| PATCH | `/tasks/{task_id}/status` | 200, 400, 401, 404, 422 |
| DELETE | `/tasks/{task_id}` | 204, 401, 404, 422 |
| GET | `/users/me` | 200, 400, 401 |
| GET | `/users/{user_id}` | 200, 400, 401, 403, 422 |
| GET | `/admin/stats` | 200, 401, 403 |
| DELETE | `/admin/tasks/{task_id}` | 204, 401, 403, 404, 422 |
| GET | `/rooms/{room_id}/users` | 200, 422 |

## WebSocket

Маршрут:

```text
/ws/rooms/{room_id}?username=alice
```

Если `username` отсутствует или состоит из пробелов, соединение закрывается с кодом `1008`.

Сообщение клиента:

```json
{
  "type": "message",
  "text": "Всем привет"
}
```

Если текст длиннее 300 символов, отправитель получает:

```json
{
  "type": "error",
  "detail": "Message is too long"
}
```

## Структура

Модели разделены по файлам в `app/models/`, роутеры разделены по доменам в `app/routers/`, общие зависимости находятся в `app/dependencies.py`, in-memory хранилище задач находится в `app/storage.py`.
