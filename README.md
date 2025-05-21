# TODO: Интеграция анализа сообщений через YandexGPT

## ✅ Сделано

- [x] Создан модуль `analytics.py` с вызовом YandexGPT
- [ ] Загружены настройки из `.env` через `configs.py`

   ```
   YANDEX_API_KEY=your-yandex-api-key
   DATABASE_URL=postgresql://user:password@host/dbname
   ```

- [x] Реализована функция `analyze_chat_messages` (выборка, анализ, запись в БД)
   - [ ] Добавить таблицу chat_analytics

   ```
    CREATE TABLE chat_analytics (
    id SERIAL PRIMARY KEY,
    analyzed_at TIMESTAMP NOT NULL,
    result TEXT NOT NULL
    );
   ```

- [x] Создан обработчик `handlers/analyze.py` с командой `/analyze_chat`
- [x] Подключение хендлера в `main.py` через `include_router`
- [x] Добавлена поддержка asyncpg, aiohttp, dotenv в зависимости

## 🔲 Что можно сделать

### 📦 Инфраструктура

- [ ] Создать файл `.env.example` с описанием переменных
- [ ] Добавить `DATABASE_URL` и `YANDEX_API_KEY` в `.env`
- [ ] Добавить `chat_analytics` через Alembic миграцию

### 🔒 Безопасность

- [ ] Ограничить команду `/analyze_chat` фильтром по user_id (только для админов)

### ⏱ Автоматизация

- [ ] Настроить автоматический запуск анализа (через `APScheduler` или cron)
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
