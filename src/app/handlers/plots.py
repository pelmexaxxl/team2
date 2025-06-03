import io, asyncio
import matplotlib.pyplot as plt
from aiogram import Router, F
from aiogram.types import Message, InputFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.user import UserAnswer, Question, User, Role

router = Router(name="plots_router")

@router.message(F.text == "/chart_results")
async def chart_results(msg: Message, session: AsyncSession):
    q = await session.scalars(select(Question))
    questions = q.all()
    if not questions:
        await msg.answer("Опросов не найдено.")
        return

    counts = [0]*len(questions[0].options)
    for question in questions:
        answers = await session.scalars(select(UserAnswer).where(UserAnswer.question_id == question.id))
        for a in answers:
            counts[a.answer_index] += 1

    fig, ax = plt.subplots()
    ax.bar(range(len(counts)), counts)
    ax.set_xticks(range(len(counts)))
    ax.set_title("Сводный результат по последнему опросу")
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    await msg.answer_photo(InputFile(buf, filename="chart.png"))
    plt.close(fig)

@router.message(F.text.startswith("/my_dynamics"))
async def my_dynamics(msg: Message, session: AsyncSession):
    user_id = msg.from_user.id
    q = select(UserAnswer).where(UserAnswer.user_id == user_id).order_by(UserAnswer.id)
    answers = (await session.scalars(q)).all()
    if len(answers) < 2:
        await msg.answer("Недостаточно данных для графика.")
        return
    xs = list(range(len(answers)))
    ys = [a.answer_index for a in answers]
    fig, ax = plt.subplots()
    ax.plot(xs, ys, marker="o")
    ax.set_title("Ваша динамика ответов")
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    await msg.answer_photo(InputFile(buf, filename="trend.png"))
    plt.close(fig)
