# 🤖 Telegram Pulse Survey Bot

Бот для Telegram, позволяющий создавать и проходить пульс-опросы. Работает на `aiogram` 3 и PostgreSQL.

---

## 🚀 Возможности

- ✅ Добавление бота в групповой чат.
- ✅ Создание опросов с открытыми вопросами и вариантами ответа.
- ✅ Рассылка опросов участникам группы в личные сообщения.
- ✅ Прохождение опросов через команду `/poll_<id>`.
- ✅ Сохранение всех ответов в базу данных.

---

## 📁 Структура проекта

```
.
├── bot.py                  # Точка входа в Telegram-бота
├── config.py               # Конфигурация (токен, БД)
├── db.py                   # Взаимодействие с базой данных PostgreSQL
│
├── handlers/
│   ├── admin.py            # Создание опросов (FSM)
│   └── respond.py          # Прохождение опросов пользователями
│
├── services/
│   └── poll_manager.py     # Рассылка опросов участникам чата в ЛС
│
└── README.md               # Описание проекта
```

---

## 🛠️ Установка и запуск

1. Установи зависимости:

```bash
pip install -r requirements.txt
```

2. Создай базу данных PostgreSQL и таблицы:

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

CREATE TABLE answers (
    id SERIAL PRIMARY KEY,
    user_id BIGINT,
    question_id INTEGER REFERENCES questions(id),
    text TEXT
);

CREATE TABLE users (
    id BIGINT PRIMARY KEY
);

CREATE TABLE chat_members (
    chat_id BIGINT,
    user_id BIGINT REFERENCES users(id),
    PRIMARY KEY (chat_id, user_id)
);
```

3. Укажи настройки в `config.py`:

```python
BOT_TOKEN = "your_token_here"
DB_CONFIG = {
    "dbname": "db_name",
    "user": "db_user",
    "password": "db_pass",
    "host": "localhost",
    "port": 5432
}
```

4. Запусти бота:

```bash
python bot.py
```

---

## 📌 Использование

- `/create_poll` — начать создание нового опроса (FSM).
- `/poll_<id>` — пройти конкретный опрос (отправляется в ЛС).

Для рассылки:

```python
from services.poll_manager import send_poll_to_users
await send_poll_to_users(bot, chat_id=123456, poll_id=1)
```

---

## 🔧 Планы по доработке

- [ ] Поддержка нескольких вопросов в одном опросе
- [ ] Просмотр статистики
- [ ] Ограничение на однократное прохождение
- [ ] Панель администратора

---

Сделано с ❤️ на aiogram



---
---

# Не уверен, что все, что ниже еще актуально)

# ✅ Что реализовано:

✅ Создание опросов

    Команда /create_poll запускает FSM-сценарий создания опроса.

    Бот пошагово запрашивает:

        Заголовок

        Описание

        Вопрос (один пока)

        Тип вопроса (открытый или с вариантами)

        Варианты ответа (если выбраны)

    Всё сохраняется в базу данных.

✅ Поддержка двух типов вопросов

    Открытые ответы — пользователь вводит текст.

    Закрытые ответы — выбирает один из предложенных вариантов.

✅ Сохранение в БД

    Сохраняются:

        Опросы

        Вопросы

        Варианты ответов

    Подключение к PostgreSQL через psycopg2.

✅ Рассылка опросов в ЛС

    В services/poll_manager.py реализована функция:

        Получает всех пользователей из чата (через chat_members)

        Пытается отправить каждому сообщение с приглашением пройти опрос

✅ Структура проекта и конфигурация

    Разделение на модули: handlers, services, db

    main.py запускает бота, регистрирует команды

    config.py содержит токен и настройки БД

## ❗Что пока не реализовано (но можно сделать быстро):

❗Прохождение опроса пользователями (ответы)

❗Сохранение результатов прохождения

❗Просмотр результатов

❗Добавление нескольких вопросов в одном опросе

❗Обработка команды /start с приветствием

❗Автоматическое добавление пользователей в users и chat_members при добавлении бота в чат


