from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User, Role

router = Router(name="cabinet_router")

@router.message(lambda m: m.text == "/cabinet")
async def cabinet(msg: Message, session: AsyncSession):
    user: User | None = await session.scalar(select(User).where(User.tg_id == msg.from_user.id))
    if not user:
        await msg.answer("Вы ещё не зарегистрированы. Нажмите /start.")
        return

    kb = []
    if user.role in (Role.HR, Role.ADMIN):
        kb.append([InlineKeyboardButton(text="📊 Итоги опросов", callback_data="cab_results")])
        kb.append([InlineKeyboardButton(text="💬 Настройки приветствия", callback_data="cab_welcome")])
    if user.role == Role.ADMIN:
        kb.append([InlineKeyboardButton(text="⚙️ Глобальные настройки", callback_data="cab_global")])

    kb.append([InlineKeyboardButton(text="🗳️ Мои ответы", callback_data="cab_my")])
    await msg.answer(f"Ваш ранг: <b>{user.role.value}</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="HTML")
