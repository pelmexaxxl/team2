import io
import matplotlib.pyplot as plt
from aiogram import Router, F
from aiogram.types import Message
from aiogram.types.input_file import BufferedInputFile  # Изменение здесь
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import UserAnswer, Question

router = Router(name="plots_router")

@router.message(F.text == "/chart_results")
async def chart_results(msg: Message, session: AsyncSession):
    # Получаем последний вопрос
    q = await session.scalars(select(Question).order_by(Question.id.desc()).limit(1))
    question = q.first()
    
    if not question:
        await msg.answer("Опросов не найдено.")
        return
    
    # Инициализируем счетчики
    counts = [0] * len(question.options)
    
    # Получаем все ответы на этот вопрос
    answers = await session.scalars(
        select(UserAnswer).where(UserAnswer.question_id == question.id)
    )
    answers = answers.all()
    
    # Считаем ответы
    for answer in answers:
        if 0 <= answer.answer_index < len(counts):
            counts[answer.answer_index] += 1
    
    # Создаем график
    fig, ax = plt.subplots()
    ax.bar(question.options, counts)
    ax.set_title(f"Результаты опроса: {question.text}")
    ax.set_ylabel("Количество ответов")
    
    # Сохраняем в буфер
    buf = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    
    # Создаем BufferedInputFile вместо InputFile
    photo = BufferedInputFile(buf.getvalue(), filename="chart.png")
    
    # Отправляем
    await msg.answer_photo(photo)
    
    # Закрываем ресурсы
    plt.close(fig)
    buf.close()

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
    await msg.answer_photo(BufferedInputFile(buf.getvalue(), filename="trend.png"))
    plt.close(fig)
