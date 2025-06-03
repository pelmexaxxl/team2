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

## Функционал

### Команды бота:

### Базовые

* **`/start`** (ЛС, все) — регистрация пользователя и приветствие.
* **`/help`** (группа / ЛС, все) — краткая справка и список основных команд.

### Управление сбором и анализом сообщений (группы)

* **`/start_collecting`** (HR / Admin) — включить запись всех сообщений в данном чате.
* **`/stop_collecting`** (HR / Admin) — выключить сбор сообщений.
* **`/analyze_chat`** (все) — ИИ-анализ сообщений этого чата за последние 24 ч.
* **`/ask_chat_gpt [часы]`** (все) — задать вопрос Yandex GPT по сообщениям чата за N часов (по умолчанию 24).
* **`/analyze_all_chats`** (Admin) — анализ сразу по всем чатам.

### Опросы и настроение

* **`/create_poll`** (HR / Admin, ЛС) — мастер создания опроса. __Странно работает__
* **`/save_template`** (HR / Admin, ЛС) — сохранить текущий черновик опроса как шаблон. *(новое)* ?
* **`/use_template <id>`** (HR / Admin, ЛС) — загрузить шаблон опроса по ID. *(новое)* ?
* **`/send_poll`** (HR, ЛС) — разослать последний созданный опрос всем сотрудникам.
* **`/poll_<id>`** (динамическая) — вручную пройти опрос по конкретному ID.
* **`/results`** (HR, ЛС) — текстовая сводка по последнему опросу.
* **`/chart_results`** (HR / Admin, ЛС) — PNG-диаграмма итогов последнего опроса. *(новое)*
* **`/my_dynamics`** (сотрудник, ЛС) — личный график изменения ответов во времени. *(новое)*
* **`/analis`** (HR, ЛС) — быстрая сводка эмоционального состояния сотрудников.

### Настройка групп

* **`/set_welcome <текст>`** (HR / Admin, группа) — задать приветствие; в тексте используйте `{user}` для автоподстановки имени. *(новое)*

### Личный кабинет

* **`/cabinet`** (ЛС / группа, все) — открыть inline-меню управления ботом; набор пунктов зависит от роли. *(новое)*


> *«новое»* — команды, добавленные в текущем релизе.
> Права доступа основываются на ролях `EMPLOYEE`, `HR`, `ADMIN`, определённых в модели `User`.


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
