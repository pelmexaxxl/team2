# src/app/services/summary.py
from aiogram import Bot           # ← добавьте эту строку
from datetime import datetime
from sqlalchemy import select, func

from app.models.user import User, Role, UserAnswer

async def send_daily_summary(bot: Bot, session_maker):
    async with session_maker() as session:
        # простой пример ― количество сотрудников с плохим/норм/хорошим настроением
        stmt = select(User.username, func.sum(UserAnswer.answer_index).label("score")).join(
            UserAnswer, User.tg_id == UserAnswer.user_id).group_by(User.tg_id)
        res = await session.execute(stmt)
        bad, mid, good = 0, 0, 0
        for _, s in res:
            if s <= 7: bad += 1
            elif s <= 12: mid += 1
            else: good += 1
        text = (f"📈 Сводка за {datetime.utcnow():%d.%m.%Y}\n"
                f"🔴 Плохое: {bad}\n🟡 Нейтральное: {mid}\n🟢 Хорошее: {good}")
        admins = await session.scalars(select(User).where(User.role == Role.HR))
        for hr in admins:
            await bot.send_message(hr.tg_id, text)
