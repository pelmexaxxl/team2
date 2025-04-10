from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.admin import create_poll, add_question_to_poll
from app.models.user import Question, Poll, User, UserAnswer
from sqlalchemy import func

router = Router()

class CreatePollFSM(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_question_text = State()
    waiting_for_question_type = State()
    waiting_for_options = State()
    waiting_for_add_another = State()  # Новое состояние
    confirming = State()
    end_questions = State()


@router.message(F.text == "/create_poll")
async def cmd_create_poll(msg: Message, state: FSMContext):
    await msg.answer("Введите заголовок опроса:")
    await state.set_state(CreatePollFSM.waiting_for_title)


@router.message(CreatePollFSM.waiting_for_title)
async def process_description(msg: Message, state: FSMContext):
    await state.update_data(title=msg.text)
    await msg.answer("Введите текст вопроса:")
    await state.set_state(CreatePollFSM.waiting_for_question_text)


# @router.message(CreatePollFSM.waiting_for_question_text)
# async def process_question_text(msg: Message, state: FSMContext):
#     await state.update_data(question_text=msg.text)
#     kb = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="Открытый ответ", callback_data="open")],
#         [InlineKeyboardButton(text="С вариантами", callback_data="closed")]
#     ])
#     await msg.answer("Выберите тип вопроса:", reply_markup=kb)
#     await state.set_state(CreatePollFSM.waiting_for_question_type)


@router.message(CreatePollFSM.waiting_for_question_text)
async def process_question_type(msg: Message, state: FSMContext):
    # if cb.data == "closed":
    await state.update_data(current_question_text=msg.text)
    await msg.answer("Введите варианты ответа через запятую:")
    await state.set_state(CreatePollFSM.waiting_for_options)
    # else:
    #     await state.set_state(CreatePollFSM.confirming)
    #     await confirm_poll(cb.message, state)


@router.message(CreatePollFSM.waiting_for_options)
async def process_options(msg: Message, state: FSMContext):
    data = await state.get_data()
    
    # Сохраняем вопрос и варианты ответов
    new_question = {
        "text": data["current_question_text"],
        "options": [opt.strip() for opt in msg.text.split(",")]
    }
    
    # Добавляем вопрос в список
    questions = data.get("questions", [])
    questions.append(new_question)
    await state.update_data(questions=questions, current_question_text=None)
    
    # Предлагаем добавить еще вопрос
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="add_another_yes"),
         InlineKeyboardButton(text="Нет", callback_data="add_another_no")]
    ])
    await msg.answer("Хотите добавить еще один вопрос?", reply_markup=keyboard)
    await state.set_state(CreatePollFSM.waiting_for_add_another)


@router.callback_query(CreatePollFSM.waiting_for_add_another, F.data.startswith("add_another_"))
async def handle_add_another(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[-1]
    print(action, flush=True)
    
    if action == "yes":
        await callback.message.answer("Введите текст следующего вопроса:")
        await state.set_state(CreatePollFSM.waiting_for_question_text)
    else:
        result = []
        data = await state.get_data()
        questions = data.get("questions", [])
        for i, q in enumerate(questions, start=1):
            q_text = f"*Вопрос {i}:* {q['text']}"
            if q["options"]:
                opts = "\n".join(f"    {j+1}) {opt}" for j, opt in enumerate(q["options"]))
                q_text += f"\n{opts}"
            else:
                q_text += "\n    (Открытый ответ)"
            result.append(q_text)
        await callback.message.answer(
        "\n\n".join(result) + "\n\nПроверьте, всё ли правильно.\n\nОтветьте *да* чтобы сохранить или *нет* чтобы добавить ещё вопросы.",
        parse_mode="Markdown"
    )
        await state.set_state(CreatePollFSM.end_questions)    
    await callback.answer()
    await callback.message.delete() 
    


@router.message(CreatePollFSM.end_questions)
async def create_poll(msg: Message, state: FSMContext, session: AsyncSession):
    await msg.answer("Переходим к созданию опроса")
    await state.set_state(CreatePollFSM.confirming)
    await confirm_poll(msg, state, session)


async def confirm_poll(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    
    # Создаем опрос
    new_poll = Poll(
        title=data["title"],
        questions=[]
    )
    
    # Добавляем вопросы с вариантами
    for question in data["questions"]:
        new_question = Question(
            text=question["text"],
            options=question["options"],
            poll_id=new_poll,
        )
        print(new_question)
        new_poll.questions.append(new_question)
    
    
    session.add(new_poll)
    await session.commit()
    
    await message.answer(f"Опрос '{new_poll.title}' успешно создан! ")
    await state.clear()


@router.message(F.text == "/analis")
async def analis(msg: Message, session: AsyncSession):
    query = (
        select(
            User.username,
            func.sum(UserAnswer.answer_index).label('total_answer_index')
        )
        .join(UserAnswer, User.tg_id == UserAnswer.user_id)
        .group_by(User.tg_id)
    )

    result = await session.execute(query)
    bad_employees, middle_employees, good_employees = [], [], []
    for username, total_index in result.all():
        if total_index <= 7:
            bad_employees.append(username)
        elif total_index <= 12:
            middle_employees.append(username)
        else:
            good_employees.append(username)
    response_message = (
            "Результаты опроса по эмоциональному состоянию сотрудников:\n\n"
            "🔴 Плохое состояние (балл <= 7):\n" + "\n".join(bad_employees) + "\n\n"
            "🟡 Нейтральное состояние (балл <= 12):\n" + "\n".join(middle_employees) + "\n\n"
            "🟢 Хорошее состояние (балл > 12):\n" + "\n".join(good_employees)
        )

        # Отправляем результаты в Telegram
    await msg.answer(response_message)
