from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from app.services.analytics import analyze_chat_messages

router = Router()

@router.message(Command("analyze_chat"))
async def handle_analyze(message: Message):
    await message.answer("Анализирую чат за последние сутки...")
    try:
        result = await analyze_chat_messages()
        await message.answer(result)
    except Exception as e:
        await message.answer(f"Ошибка: {e}")
