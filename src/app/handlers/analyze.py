from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
import asyncpg
from app.services.analytics import analyze_chat_messages, ask_chat_messages_gpt
from app.configs import settings
import logging
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.state import State, StatesGroup
from app.models.user import User, Role


router = Router(name="analyze_router")
logger = logging.getLogger(__name__)


# Определяем состояния для FSM
class AskGPTForm(StatesGroup):
    waiting_for_question = State()


@router.message(Command("analyze_chat"))
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


@router.message(Command("analyze_all_chats"))
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


@router.message(Command("ask_chat_gpt"))
async def handle_ask_chat_gpt(message: Message, state: FSMContext):
    """Start process of asking YandexGPT about chat messages."""
    logger.info(f"Received ask_chat_gpt command in chat {message.chat.id}")
    
    # Extract hours parameter if provided
    command_parts = message.text.split()
    hours = 24  # Default 24 hours
    
    if len(command_parts) > 1:
        try:
            hours = int(command_parts[1])
            if hours < 1:
                hours = 1
            elif hours > 168:  # max 7 days
                hours = 168
        except ValueError:
            pass
    
    await state.update_data(chat_id=message.chat.id, hours=hours)
    await state.set_state(AskGPTForm.waiting_for_question)
    await message.answer(
        f"Введите ваш вопрос для анализа сообщений из чата за последние {hours} часов.\n"
        "Например: 'Какие темы обсуждались в чате?', 'Найди интересные идеи' и т.д."
    )


@router.message(AskGPTForm.waiting_for_question)
async def process_question(message: Message, state: FSMContext):
    """Process the question and send it with chat messages to YandexGPT."""
    if not message.text:
        await message.answer("Пожалуйста, введите текстовый вопрос.")
        return
    
    data = await state.get_data()
    chat_id = data.get('chat_id')
    hours = data.get('hours', 24)
    question = message.text
    
    logger.info(f"Received question for chat {chat_id}: {question}")
    
    # Clear state
    await state.clear()
    
    await message.answer(f"Отправляю ваш вопрос вместе с сообщениями из чата за последние {hours} часов в Яндекс ГПТ...")
    
    try:
        result = await ask_chat_messages_gpt(chat_id, question, hours)
        
        # Разбиваем длинный ответ на части, если нужно
        max_message_length = 4000
        if len(result) > max_message_length:
            parts = [result[i:i+max_message_length] for i in range(0, len(result), max_message_length)]
            for i, part in enumerate(parts):
                await message.answer(f"Часть {i+1}/{len(parts)}:\n{part}")
        else:
            await message.answer(result)
            
        logger.info(f"Successfully sent answer for chat {chat_id}")
    except Exception as e:
        logger.error(f"Error sending question to Yandex GPT: {e}", exc_info=True)
        await message.answer(f"Произошла ошибка при запроса: {str(e)}")


@router.message(Command("analyze_result"))
async def handle_analyze_result(
    message: Message,
    session: AsyncSession,
):
    # Проверяем, что команда вызвана в личных сообщениях
    if message.chat.type != "private":
        await message.answer("Эта команда доступна только в личных сообщениях.")
        return

    # Получаем информацию о пользователе
    user = await session.get(User, message.from_user.id)
    
    # Проверяем роль пользователя
    if not user or user.role not in [Role.HR, Role.ADMIN]:
        await message.answer("Доступ запрещен. Требуется роль HR или Admin.")
        return

    # Проверяем, передан ли chat_id в команде
    if not message.text or len(message.text.split()) < 2:
        await message.answer("Использование: /analyze_result <chat_id>")
        return

    try:
        chat_id = int(message.text.split()[1])
    except ValueError:
        await message.answer("Некорректный chat_id. Укажите числовой идентификатор чата.")
        return

    # Получаем последний результат анализа для указанного чата
    conn = await asyncpg.connect(settings.database_url)
        # Получаем последний результат анализа для указанного чата
    row = await conn.fetchrow("""
        SELECT analyzed_at, result
        FROM chat_analytics
        WHERE chat_id = $1
        ORDER BY analyzed_at DESC
        LIMIT 1
    """, chat_id)

    if not row:
        await message.answer(f"Нет данных анализа для чата {chat_id}.")
        return

    # Форматируем ответ
    chat_info = f"Чат ID: {chat_id}"
    response = (
        f"📊 Анализ чата: {chat_info}\n"
        f"🕒 Время анализа: {row['analyzed_at']}\n"
        f"📝 Результат:\n{row['result']}"
    )

    await message.answer(response)


@router.message(Command("get_chat_id"))
async def get_chat_id_handler(message: Message):
    """Обработчик для получения ID текущего чата"""
    chat_id = message.chat.id
    chat_type = message.chat.type
    
    # Определяем тип чата для понятного вывода
    chat_type_name = {
        "private": "личные сообщения",
        "group": "групповой чат",
        "supergroup": "супергруппа",
        "channel": "канал"
    }.get(chat_type, "неизвестный тип чата")
    
    response = (
        f"📌 Информация о текущем чате:\n"
        f"🆔 ID чата: <code>{chat_id}</code>\n"
        f"📝 Тип чата: {chat_type_name}\n"
        f"👥 Название: {message.chat.title or 'Нет названия'}"
    )
    
    await message.answer(response, parse_mode="HTML")