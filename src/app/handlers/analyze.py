from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from app.services.analytics import analyze_chat_messages
from app.configs import settings
import logging


router = Router(name="analyze_router")
logger = logging.getLogger(__name__)


@router.message(F.text.startswith("/analyze_chat"))
async def handle_analyze(message: Message):
    """Analyze messages in the current chat."""
    logger.info(f"Received analyze_chat command in chat {message.chat.id}")
    await message.answer("Анализирую чат за последние сутки...")
    try:
        result = await analyze_chat_messages(message.chat.id)
        await message.answer(result)
        logger.info(f"Completed analysis for chat {message.chat.id}")
    except Exception as e:
        logger.error(f"Error analyzing chat {message.chat.id}: {e}", exc_info=True)
        await message.answer(f"Ошибка при анализе: {e}")


@router.message(F.text.startswith("/analyze_all_chats"))
async def handle_analyze_all(message: Message):
    """Analyze messages in all chats (admin only)."""
    logger.info(f"Received analyze_all_chats command from user {message.from_user.id}")
    
    # Check if user is admin
    if not message.from_user or message.from_user.id != int(settings.ADMIN_USER_ID):
        logger.warning(f"User {message.from_user.id} tried to use admin command analyze_all_chats")
        await message.answer("Эта команда доступна только администратору.")
        return
        
    await message.answer("Запускаю анализ всех чатов...")
    try:
        result = await analyze_chat_messages()
        await message.answer(result)
        logger.info("Completed analysis for all chats")
    except Exception as e:
        logger.error(f"Error analyzing all chats: {e}", exc_info=True)
        await message.answer(f"Ошибка при анализе: {e}")
