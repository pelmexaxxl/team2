from datetime import datetime, timedelta
from sqlalchemy import select
from aiogram import Bot

from app.models.user import User, Role, UserAnswer, Question
from app.models.extras import Reminder

REMINDER_DELAY = timedelta(hours=6)

async def check_and_send(bot: Bot, session_maker):
    """Проверяем, кто не прошёл активный опрос, и шлём им напоминание."""

    async with session_maker() as session:
        # берём последние активные опросы
        q = select(Question.poll_id).distinct().order_by(Question.poll_id.desc()).limit(1)
        poll_id = (await session.scalar(q))
        if not poll_id:
            return

        # уже отвечавшие
        answered = select(UserAnswer.user_id).where(UserAnswer.question_id.in_(
            select(Question.id).where(Question.poll_id == poll_id)
        ))
        answered_ids = {row[0] async for row in session.stream(answered)}

        employees = (await session.scalars(select(User).where(User.role == Role.EMPLOYEE))).all()
        need_remind = [u for u in employees if u.tg_id not in answered_ids]

        # проверяем, не слали ли уже
        for emp in need_remind:
            exists = await session.scalar(
                select(Reminder.id).where(Reminder.poll_id == poll_id,
                                        Reminder.created_at >= datetime.utcnow() - REMINDER_DELAY,
                                        Reminder.is_done == False)  # noqa
            )
            if exists:
                continue
            await bot.send_message(emp.tg_id, "Напоминание: пожалуйста, пройдите текущий опрос.")
        # ---- 4. фиксируем факт рассылки одного «пакета» напоминаний ---
        session.add(Reminder(poll_id=poll_id))
        await session.commit()
