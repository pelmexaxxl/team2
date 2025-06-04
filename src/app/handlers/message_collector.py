from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
import asyncpg
import logging
from app.configs import settings


# Создаем роутер с низким приоритетом для сбора сообщений
router = Router(name="message_collector")
logger = logging.getLogger(__name__)


@router.message(F.text.startswith("/start_collecting"))
async def start_collecting(message: Message):
    """Start collecting messages in this chat."""
    logger.info(f"Received start_collecting command in chat {message.chat.id}")
    if message.chat.type == "private":
        await message.answer("Эта команда работает только в группах и каналах.")
        return

    conn = await asyncpg.connect(settings.database_url)
    try:
        await conn.execute(
            """
            INSERT INTO chat_settings (chat_id, collect_messages)
            VALUES ($1, true)
            ON CONFLICT (chat_id) DO UPDATE
            SET collect_messages = true
            """,
            message.chat.id
        )
        await message.answer("Бот начал собирать сообщения в этом чате.")
        logger.info(f"Started collecting messages in chat {message.chat.id}")
    except Exception as e:
        logger.error(f"Error starting collection: {e}")
        await message.answer("Произошла ошибка при настройке сбора сообщений.")
    finally:
        await conn.close()


@router.message(F.text.startswith("/stop_collecting"))
async def stop_collecting(message: Message):
    """Stop collecting messages in this chat."""
    logger.info(f"Received stop_collecting command in chat {message.chat.id}")
    if message.chat.type == "private":
        await message.answer("Эта команда работает только в группах и каналах.")
        return

    conn = await asyncpg.connect(settings.database_url)
    try:
        await conn.execute(
            """
            UPDATE chat_settings
            SET collect_messages = false
            WHERE chat_id = $1
            """,
            message.chat.id
        )
        await message.answer("Бот прекратил сбор сообщений в этом чате.")
        logger.info(f"Stopped collecting messages in chat {message.chat.id}")
    except Exception as e:
        logger.error(f"Error stopping collection: {e}")
        await message.answer("Произошла ошибка при остановке сбора сообщений.")
    finally:
        await conn.close()


# Для отладки - обработчик помощи
@router.message(F.text.startswith("/help"))
async def help_command(message: Message):
    """Show help information."""
    logger.info(f"Received help command in chat {message.chat.id}")
    help_text = """
🌟 Базовые команды:

/start (ЛС, все) — 🎉 регистрация пользователя и приветствие.

/help (группа / ЛС, все) — ℹ️ краткая справка и список основных команд.

✁ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

🔍 Управление сбором и анализом сообщений (группы):
/start_collecting (HR / Admin) — 📝 включить запись всех сообщений в чате.

/stop_collecting (HR / Admin) — 🚫 выключить сбор сообщений.

/analyze_chat (все) — 📊 ИИ-анализ сообщений чата за последние 24 ч.

/ask_chat_gpt [часы] (все) — 🤖 задать вопрос Yandex GPT по сообщениям чата за N часов (по умолчанию 24).

/analyze_all_chats (Admin) — 📈 анализ всех чатов одновременно.

✁ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

📊 Опросы и настроение:

/create_poll (HR / Admin, ЛС) — 🛠️ мастер создания опроса.

/save_template (HR / Admin, ЛС) — 💾 сохранить текущий черновик опроса как шаблон. * NEW

/use_template <id> (HR / Admin, ЛС) — 🗂️ загрузить шаблон опроса по ID.  * NEW

/send_poll (HR, ЛС) — 📬 разослать последний созданный опрос всем сотрудникам.

/poll_<id> (динамическая) — 📝 пройти опрос по конкретному ID.

/results (HR, ЛС) — 📋 текстовая сводка по последнему опросу.

/chart_results (HR / Admin, ЛС) — 📊 PNG-диаграмма итогов последнего опроса. * NEW

/my_dynamics (сотрудник, ЛС) — 📈 личный график изменения ответов во времени. * NEW

/analis (HR, ЛС) — 🧠 быстрая сводка эмоционального состояния сотрудников.

✁ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

⚙️ Настройка групп:
/set_welcome <текст> (HR / Admin, группа) — 👋 задать приветствие; в тексте используйте {user} для автоподстановки имени. * NEW

✁ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

🧑‍💼 Личный кабинет:
/cabinet (ЛС / группа, все) — 🔧 открыть inline-меню управления ботом; набор пунктов зависит от роли. * NEW

✁ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Права доступа основываются на ролях EMPLOYEE, HR, ADMIN, определённых в модели User.

*новое — команды, добавленные в текущем релизе.
"""
    await message.answer(help_text)


# Общий обработчик для всех сообщений - убрали F.text и flags
@router.message()
async def collect_message(message: Message):
    """Collect user messages."""
    # Вывод диагностической информации для всех сообщений
    logger.info(f"RECEIVED MESSAGE in chat {message.chat.id} from {getattr(message.from_user, 'username', 'unknown')} or id {getattr(message.from_user, 'id', 'unknown')}")
    
    # Skip private chats and bot commands
    if message.chat.type == "private":
        logger.info("Skipping private chat message")
        return
        
    if message.text and message.text.startswith("/"):
        logger.info(f"Skipping command message: {message.text}")
        return
    
    # Определяем тип сообщения и его содержимое
    content = ""
    if message.text:
        content = message.text
    else:
        logger.info("Message has no text, skipping")
        # Можно добавить обработку других типов сообщений (фото, документы и т.д.)
        return
    
    logger.info(f"Processing message in chat {message.chat.id}")
    
    try:
        conn = await asyncpg.connect(settings.database_url)
        logger.info("Database connection established")
        
        # Check if collection is enabled for this chat
        settings_row = await conn.fetchrow(
            "SELECT collect_messages FROM chat_settings WHERE chat_id = $1",
            message.chat.id
        )
        
        if not settings_row:
            logger.info(f"No settings found for chat {message.chat.id}, initializing with default settings")
            # Если нет настроек для этого чата, создаем их (по умолчанию сбор отключен)
            await conn.execute(
                """
                INSERT INTO chat_settings (chat_id, collect_messages)
                VALUES ($1, false)
                ON CONFLICT (chat_id) DO NOTHING
                """,
                message.chat.id
            )
            await conn.close()
            return
            
        if not settings_row['collect_messages']:
            logger.info(f"Message collection is disabled for chat {message.chat.id}")
            await conn.close()
            return
        
        logger.info(f"Saving message to database from user {getattr(message.from_user, 'username', 'unknown')}")
        
        # Save the message
        await conn.execute(
            """
            INSERT INTO messages (chat_id, user_id, username, content, created_at)
            VALUES ($1, $2, $3, $4, NOW())
            """,
            message.chat.id,
            message.from_user.id,
            getattr(message.from_user, "username", None),
            content
        )
        await conn.close()
        logger.info(f"Successfully saved message from {getattr(message.from_user, 'username', message.from_user.id)} in chat {message.chat.id}")
    except Exception as e:
        logger.error(f"Error collecting message: {e}", exc_info=True)
        try:
            if 'conn' in locals() and conn:
                await conn.close()
        except Exception as close_error:
            logger.error(f"Error closing connection: {close_error}") 