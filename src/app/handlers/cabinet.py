from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func 
from app.models.user import User, Role, UserAnswer, Question
from aiogram.types import CallbackQuery

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


from aiogram.types import CallbackQuery

# --- 1. Мои ответы -------------------------------------------------
@router.callback_query(lambda c: c.data == "cab_my")
async def cab_my(cb: CallbackQuery, session: AsyncSession):
    await cb.answer()                        # закрыть «часики»
    # пример: вывести последние 5 ответов пользователя
    q = select(UserAnswer).where(UserAnswer.user_id == cb.from_user.id).order_by(UserAnswer.id.desc()).limit(5)
    answers = (await session.scalars(q)).all()
    text = "\n".join(f"• {a.answer_index} — вопрос {a.question_id}" for a in answers) or "Ответов пока нет."
    await cb.message.edit_text(f"<b>Ваши недавние ответы</b>\n{text}", parse_mode="HTML")

# --- 2. Итоги опросов ----------------------------------------------
@router.callback_query(lambda c: c.data == "cab_results")
async def cab_results(cb: CallbackQuery, session: AsyncSession):
    await cb.answer()
    # быстрая сводка: количество ответов в последнем опросе
    q_poll = select(Question.poll_id).distinct().order_by(Question.poll_id.desc()).limit(1)
    poll_id = await session.scalar(q_poll)
    if not poll_id:
        await cb.message.edit_text("Опросов ещё не проводилось.")
        return
    total = await session.scalar(
        select(func.count()).select_from(UserAnswer).where(
            UserAnswer.question_id.in_(select(Question.id).where(Question.poll_id == poll_id))
        )
    )
    await cb.message.edit_text(f"В последнем опросе получено ответов: <b>{total}</b>", parse_mode="HTML")

# --- 3. Настройка приветствия --------------------------------------
@router.callback_query(lambda c: c.data == "cab_welcome")
async def cab_welcome(cb: CallbackQuery):
    await cb.answer()
    await cb.message.edit_text(
        "Отправьте\n```\n/set_welcome Привет, {user}!\n```\nв группе, чтобы изменить приветственное сообщение."
    )

# --- 4. Глобальные настройки (пример) ------------------------------
@router.callback_query(lambda c: c.data == "cab_global")
async def cab_global(cb: CallbackQuery):
    await cb.answer()
    await cb.message.edit_text(
        "Панель глобальных настроек пока не реализована. Напишите разработчику 😉"
    )
