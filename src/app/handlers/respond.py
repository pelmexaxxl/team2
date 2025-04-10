from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import get_poll, get_questions, get_options, save_answer

router = Router()

class PollResponse(StatesGroup):
    poll_id = State()
    question_index = State()
    answers = State()

@router.message(F.text.startswith("/poll_"))
async def start_poll(message: Message, state: FSMContext):
    try:
        poll_id = int(message.text.split("_")[1])
    except (IndexError, ValueError):
        await message.answer("Неверная команда.")
        return

    poll = get_poll(poll_id)
    if not poll:
        await message.answer("Опрос не найден.")
        return

    questions = get_questions(poll_id)
    if not questions:
        await message.answer("У опроса нет вопросов.")
        return

    await state.update_data(poll_id=poll_id, question_index=0, answers={})
    await ask_question(message, state, questions)

async def ask_question(message: Message, state: FSMContext, questions):
    data = await state.get_data()
    index = data["question_index"]

    if index >= len(questions):
        answers = data["answers"]
        for q_id, text in answers.items():
            save_answer(user_id=message.from_user.id, question_id=q_id, text=text)
        await state.clear()
        await message.answer("Спасибо за прохождение опроса!")
        return

    question = questions[index]
    text = f"Вопрос {index + 1}/{len(questions)}:\n{question['text']}"
    if question['is_open']:
        await state.set_state(PollResponse.answers)
        await message.answer(text)
    else:
        options = get_options(question['id'])
        option_text = "\n".join([f"{i+1}. {opt['text']}" for i, opt in enumerate(options)])
        await state.set_state(PollResponse.answers)
        await message.answer(f"{text}\n\n{option_text}")

@router.message(PollResponse.answers)
async def handle_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    index = data["question_index"]
    poll_id = data["poll_id"]
    questions = get_questions(poll_id)
    question = questions[index]

    answers = data.get("answers", {})
    answers[question["id"]] = message.text
    await state.update_data(answers=answers, question_index=index + 1)

    await ask_question(message, state, questions)
