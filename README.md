# 🤖 PulseBot — Telegram бот для пульс-опросов

PulseBot — это телеграм-бот, созданный с помощью [aiogram](https://docs.aiogram.dev), который позволяет создавать, отправлять и проходить анонимные (или нет) пульс-опросы прямо в Telegram.

---

## 🚀 Возможности

- ✅ Добавление бота в чаты/группы
- ✅ Отправка личных сообщений участникам чата с приглашением пройти опрос
- ✅ Создание кастомных опросов
  - Вопросы с открытым ответом
  - Вопросы с выбором из вариантов
- ✅ Хранение и отображение результатов
- ✅ FSM логика для пошагового создания опросов

---

## 🗂 Структура проекта

```
pulse_bot/
├── main.py                # Точка входа, инициализация бота и диспетчера
├── config.py              # Конфигурация токена и базы данных
├── db.py                  # Работа с базой данных (PostgreSQL)
├── handlers/
│   ├── __init__.py        # Инициализация роутеров
│   └── admin.py           # FSM-хендлеры для создания опросов
├── services/
│   └── poll_manager.py    # Рассылка опросов пользователям из чатов
```

---

## 🧠 Описание файлов

### `main.py`
Запускает бота, регистрирует роутеры, настраивает команды, стартует `Dispatcher` с `MemoryStorage`.

### `config.py`
Содержит:
- `TOKEN` — токен Telegram-бота
- `DB_CONFIG` — параметры подключения к PostgreSQL

### `db.py`
Модуль взаимодействия с БД. Реализует:
- `create_poll()` — создание опроса
- `add_question_to_poll()` — добавление вопроса
- `add_option_to_question()` — добавление варианта ответа
- `get_users_in_chat()` — получить всех участников беседы

### `handlers/admin.py`
FSM-хендлеры для создания опросов:
- `/create_poll` — запуск создания опроса
- FSM: заголовок → описание → вопрос → тип → варианты → подтверждение

### `services/poll_manager.py`
Рассылает личные сообщения с приглашением пройти опрос участникам чата.

---

## 🛠 Требования

- Python 3.10+
- PostgreSQL
- `aiogram >= 3.x`

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Пример `requirements.txt`
```
aiogram
psycopg2-binary
```

---

## 🗃 SQL: структура базы данных (пример)
```sql
CREATE TABLE polls (
    id SERIAL PRIMARY KEY,
    title TEXT,
    description TEXT,
    creator_id BIGINT
);

CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    poll_id INTEGER REFERENCES polls(id),
    text TEXT,
    is_open BOOLEAN
);

CREATE TABLE options (
    id SERIAL PRIMARY KEY,
    question_id INTEGER REFERENCES questions(id),
    text TEXT
);

CREATE TABLE users (
    id BIGINT PRIMARY KEY
);

CREATE TABLE chat_members (
    chat_id BIGINT,
    user_id BIGINT REFERENCES users(id)
);
```

---

## 📩 Контакт
Если хочешь расширить функциональность — просто напиши 😉

