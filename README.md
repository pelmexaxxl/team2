# Интеграция анализа сообщений через YandexGPT

## ✅ Сделано

- [x] Создан модуль `analytics.py` с вызовом YandexGPT
- [x] Загружены настройки из `.env` через `configs.py`

   ```
   YANDEX_API_KEY=your-yandex-api-key
   DATABASE_URL=postgresql://user:password@host/dbname
   ADMIN_USER_ID=123456789
   ```

- [x] Реализована функция `analyze_chat_messages` (выборка, анализ, запись в БД)
- [x] Добавлены таблицы для сообщений и анализа
   ```
    CREATE TABLE chat_settings (
      chat_id BIGINT PRIMARY KEY,
      collect_messages BOOLEAN NOT NULL DEFAULT false,
      last_analyzed TIMESTAMP
    );

    CREATE TABLE messages (
      id BIGINT PRIMARY KEY,
      chat_id BIGINT NOT NULL,
      user_id BIGINT NOT NULL REFERENCES users(tg_id),
      username VARCHAR(64),
      content TEXT NOT NULL,
      created_at TIMESTAMP NOT NULL DEFAULT NOW()
    );

    CREATE TABLE chat_analytics (
      id BIGINT PRIMARY KEY,
      chat_id BIGINT NOT NULL,
      analyzed_at TIMESTAMP NOT NULL DEFAULT NOW(),
      result TEXT NOT NULL
    );
   ```

- [x] Создан обработчик `handlers/analyze.py` с командой `/analyze_chat`
- [x] Создан обработчик `handlers/message_collector.py` для сбора сообщений в чатах
- [x] Подключение хендлеров в `main.py` через `include_router`
- [x] Добавлена поддержка asyncpg, aiohttp, dotenv в зависимости
- [x] Добавлен функционал автоматического анализа сообщений в конце дня

## 📋 Новый функционал: Сбор и анализ сообщений

### Команды бота:

- `/start_collecting` - Начать сбор сообщений в текущем чате
- `/stop_collecting` - Остановить сбор сообщений в текущем чате
- `/analyze_chat` - Проанализировать сообщения из текущего чата за последние сутки
- `/analyze_all_chats` - Проанализировать сообщения из всех чатов (только для админа)

### Автоматизация:

Бот автоматически анализирует все чаты с включенным сбором сообщений каждый день в 23:00 и сохраняет результаты в базу данных.

## 🔲 Что можно сделать дальше

### 📦 Инфраструктура

- [ ] Создать файл `.env.example` с описанием переменных
- [x] Добавить `chat_analytics` и другие таблицы через Alembic миграцию

### 🔒 Безопасность

- [x] Ограничить команду `/analyze_all_chats` фильтром по user_id (только для админов)

### ⏱ Автоматизация

- [x] Настроить автоматический запуск анализа (ежедневно в 23:00)
- [ ] Отправлять результат анализа в Telegram-чат/админу автоматически

---

# *Structure*

```
team2
├─ Dockerfile
├─ README.md
├─ docker-compose.yml
├─ logs
│  └─ bot_log.log
├─ requirements.txt
└─ src
   ├─ alembic
   │  ├─ README
   │  ├─ env.py
   │  ├─ script.py.mako
   │  └─ versions
   │     ├─ __pycache__
   │     │  └─ d1c5e7ce77ed_initial.cpython-312.pyc
   │     └─ d1c5e7ce77ed_initial.py
   ├─ alembic.ini
   ├─ app
   │  ├─ __init__.py
   │  ├─ configs.py
   │  ├─ db
   │  │  ├─ __init__.py
   │  │  └─ db.py
   │  ├─ db.py
   │  ├─ handlers
   │  │  ├─ __init__.py
   │  │  ├─ admin.py
   │  │  ├─ analyze.py
   │  │  ├─ respond.py
   │  │  └─ user.py
   │  ├─ main.py
   │  ├─ middlewares
   │  │  ├─ __init__.py
   │  │  └─ db.py
   │  ├─ models
   │  │  ├─ __init__.py
   │  │  ├─ base.py
   │  │  └─ user.py
   │  ├─ services
   │  │  ├─ __init__.py
   │  │  ├─ admin.py
   │  │  ├─ analytics.py
   │  │  └─ poll_manager.py
   │  └─ utils
   │     ├─ __init__.py
   │     ├─ emotions.py
   │     └─ questions.py
   └─ table_structure.sql

```
