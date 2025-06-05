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


@router.message(CreatePollFSM.waiting_for_question_text)
async def process_question_text(msg: Message, state: FSMContext):
    await state.update_data(question_text=msg.text)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открытый ответ", callback_data="open")],
        [InlineKeyboardButton(text="С варианами",  callback_data="closed")]
    ])
    await msg.answer("Выберите тип вопроса:", reply_markup=kb)
    await state.set_state(CreatePollFSM.waiting_for_question_type)


@router.callback_query(CreatePollFSM.waiting_for_question_type)
async def choose_type(cb: CallbackQuery, state: FSMContext):
    qtext = (await state.get_data())["question_text"]
    if cb.data == "open":
        # сразу добавляем без options
        questions = (await state.get_data()).get("questions", [])
        questions.append({"text": qtext, "options": []})
        await state.update_data(questions=questions)
        await ask_add_more(cb, state)                 # переиспользуем хелпер ниже
    else:
        await state.update_data(current_question_text=qtext)
        await cb.message.answer("Введите варианты через запятую:")
        await state.set_state(CreatePollFSM.waiting_for_options)
    await cb.answer()
# ───────── helper "add one more question?" ─────────────────────
async def ask_add_more(event: CallbackQuery | Message, state: FSMContext):
    """
    Показывает клавиатуру «Добавить вопрос / Готово» и
    переводит FSM в waiting_for_add_another.
    """
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить вопрос", callback_data="add_another_yes"),
         InlineKeyboardButton(text="✅ Готово",          callback_data="add_another_no")]
    ])

    # event может быть CallbackQuery или Message
    send = event.message.answer if isinstance(event, CallbackQuery) else event.answer
    await send("Хотите добавить ещё один вопрос?", reply_markup=kb)

    await state.set_state(CreatePollFSM.waiting_for_add_another)
# ───────────────────────────────────────────────────────────────


# @router.message(CreatePollFSM.waiting_for_question_text)
# async def process_question_type(msg: Message, state: FSMContext):
#     # if cb.data == "closed":
#     await state.update_data(current_question_text=msg.text)
#     await msg.answer("Введите варианты ответа через запятую:")
#     await state.set_state(CreatePollFSM.waiting_for_options)
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
            "🔴 Плохое состояние:\n" + "\n".join(bad_employees) + "\n\n"
            "🟡 Нейтральное состояние:\n" + "\n".join(middle_employees) + "\n\n"
            "🟢 Хорошее состояние:\n" + "\n".join(good_employees)
        )

        # Отправляем результаты в Telegram
    await msg.answer(response_message)

@router.message(F.text == "/save_template")
async def save_template(msg: Message, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    if not data.get("questions"):
        await msg.answer("Сначала создайте опрос через /create_poll.")
        return
    tpl = PollTemplate(
        title=data["title"],
        json_body=json.dumps(data["questions"]),
        author_id=msg.from_user.id,
        description="Создано через бот"
    )
    session.add(tpl)
    await session.commit()
    await msg.answer("✅ Шаблон сохранён!")

@router.message(F.text.startswith("/use_template"))
async def use_template(msg: Message, session: AsyncSession, state: FSMContext):
    try:
        tpl_id = int(msg.text.split()[1])
    except Exception:
        await msg.answer("Формат: /use_template <id>")
        return
    tpl = await session.get(PollTemplate, tpl_id)
    if not tpl:
        await msg.answer("Шаблон не найден.")
        return
    await state.update_data(title=tpl.title,
                            questions=json.loads(tpl.json_body))
    await msg.answer("Шаблон загружен, отправьте *да* чтобы опубликовать или *нет* для правок.", parse_mode="Markdown")
    await state.set_state(CreatePollFSM.confirming)
