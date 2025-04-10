from aiogram import Router, F, Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from aiogram.fsm.storage.memory import MemoryStorage, StorageKey

from app.models.user import User, Role, Poll, Question, UserAnswer

router = Router()

class RegisterFSM(StatesGroup):
    confirm = State()


class PollStates(StatesGroup):
    answering = State()


@router.message(F.text == "/start")
async def start_registration(msg: Message, state: FSMContext, session: AsyncSession):
    tg_id = msg.from_user.id
    username = msg.from_user.username
    user = await session.scalar(select(User).where(User.tg_id == tg_id))

    if not user:
        user = User(tg_id=tg_id, username=username, role=Role.EMPLOYEE)
        session.add(user)
        await session.commit()
        await msg.answer("Вы зарегистрированы как Сотрудник. Добро пожаловать!")
    else:
        await msg.answer(f"Добро пожаловать, {user.role.value.upper()}!")


@router.message(F.text == "/send_poll")
async def send_poll_command(msg: Message, session: AsyncSession, bot: Bot, dispatcher: Dispatcher):
    tg_id = msg.from_user.id
    hr = await session.scalar(select(User).where(User.tg_id == tg_id))

    if hr and hr.role == Role.HR:
        stmt = select(Poll).options(selectinload(Poll.questions)).order_by(Poll.id.desc())
        poll = await session.scalar(stmt)
        if not poll:
            await msg.answer("Нет активных опросов.")
            return

        employees = await session.scalars(select(User).where(User.role == Role.EMPLOYEE))
        questions_data = [
        {"id": q.id, "text": q.text, "options": q.options}
        for q in poll.questions
    ]

        for employee in employees:
            question = questions_data[0]
            options_text = "\n".join(f"{i+1}) {opt}" for i, opt in enumerate(question["options"]))
            await msg.bot.send_message(
                chat_id=employee.tg_id,
                text=f"{question['text']}\n\n{options_text}\n\nОтветьте числом."
            )
            
            storage_key = StorageKey(bot_id=bot.id, user_id=employee.tg_id, chat_id=employee.tg_id)
            employee_context = FSMContext(storage=dispatcher.storage, key=storage_key)

            await employee_context.set_data({
                "questions": questions_data,
                "current_index": 0,
                "poll_id": poll.id,
                "answers": [],
            })
            await employee_context.set_state(PollStates.answering)
        await msg.answer("Опрос разослан всем сотрудникам.")
    else:
        await msg.answer("Только HR может отправлять опросы.")


@router.message(PollStates.answering)
async def process_poll_answer(msg: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    questions = data["questions"]
    index = data["current_index"]
    answers = data["answers"]
    poll_id = data["poll_id"]

    answer_text = msg.text.strip()
    if not answer_text.isdigit() or not (1 <= int(answer_text) <= len(questions[index]["options"])):
        await msg.answer("Пожалуйста, введите номер варианта ответа.")
        return

    selected_index = int(answer_text) - 1

    answers.append({
        "question_id": questions[index]["id"],
        "selected_option": selected_index
    })

    index += 1
    if index < len(questions):
        next_question = questions[index]
        options_text = "\n".join(f"{i+1}) {opt}" for i, opt in enumerate(next_question["options"]))
        await msg.answer(
            f"{next_question['text']}\n\n{options_text}\n\nОтветьте числом."
        )
        await state.set_data({
            "questions": questions,
            "current_index": index,
            "poll_id": poll_id,
            "answers": answers,
        })
    else:
        user_id = msg.from_user.id

        for ans in answers:
            answer_obj = UserAnswer(
                user_id=user_id,
                question_id=ans["question_id"],
                answer_index=ans["selected_option"]
            )
            session.add(answer_obj)

        await session.commit()
        await msg.answer("Спасибо за прохождение опроса!")
        await state.clear()


@router.message(F.text == "/results")
async def export_results(msg: Message, session: AsyncSession):
    user = await session.scalar(select(User).where(User.tg_id == msg.from_user.id))
    if not user or user.role != Role.HR:
        await msg.answer("Только HR может просматривать результаты.")
        return

    stmt = select(Poll).options(selectinload(Poll.questions)).order_by(Poll.id.desc())
    poll = await session.scalar(stmt)
    if not poll:
        await msg.answer("Нет доступных опросов.")
        return

    text = f"Результаты по опросу: {poll.title}\n\n"
    for question in poll.questions:
        text += f"{question.text}\n"
        answers = await session.scalars(select(UserAnswer).where(UserAnswer.question_id == question.id))
        counts = [0] * len(question.options)
        for a in answers:
            counts[a.answer_index] += 1
        for i, option in enumerate(question.options):
            text += f"  {option}: {counts[i]}\n"
        text += "\n"

    await msg.answer(text)
