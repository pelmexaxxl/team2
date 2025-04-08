from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db import create_poll, add_question_to_poll, add_option_to_question

router = Router()

class CreatePollFSM(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_question_text = State()
    waiting_for_question_type = State()
    waiting_for_options = State()
    confirming = State()


@router.message(F.text == "/create_poll")
async def cmd_create_poll(msg: Message, state: FSMContext):
    await msg.answer("Введите заголовок опроса:")
    await state.set_state(CreatePollFSM.waiting_for_title)


@router.message(CreatePollFSM.waiting_for_title)
async def process_title(msg: Message, state: FSMContext):
    await state.update_data(title=msg.text)
    await msg.answer("Введите описание опроса:")
    await state.set_state(CreatePollFSM.waiting_for_description)


@router.message(CreatePollFSM.waiting_for_description)
async def process_description(msg: Message, state: FSMContext):
    await state.update_data(description=msg.text)
    await msg.answer("Введите текст первого вопроса:")
    await state.set_state(CreatePollFSM.waiting_for_question_text)


@router.message(CreatePollFSM.waiting_for_question_text)
async def process_question_text(msg: Message, state: FSMContext):
    await state.update_data(question_text=msg.text)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открытый ответ", callback_data="open")],
        [InlineKeyboardButton(text="С вариантами", callback_data="closed")]
    ])
    await msg.answer("Выберите тип вопроса:", reply_markup=kb)
    await state.set_state(CreatePollFSM.waiting_for_question_type)


@router.callback_query(CreatePollFSM.waiting_for_question_type)
async def process_question_type(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.update_data(question_type=cb.data)

    if cb.data == "closed":
        await cb.message.answer("Введите варианты ответа через запятую:")
        await state.set_state(CreatePollFSM.waiting_for_options)
    else:
        await state.set_state(CreatePollFSM.confirming)
        await confirm_poll(cb.message, state)


@router.message(CreatePollFSM.waiting_for_options)
async def process_options(msg: Message, state: FSMContext):
    await state.update_data(options=[opt.strip() for opt in msg.text.split(",")])
    await state.set_state(CreatePollFSM.confirming)
    await confirm_poll(msg, state)


async def confirm_poll(msg: Message, state: FSMContext):
    data = await state.get_data()
    poll_id = create_poll(title=data['title'], description=data['description'], creator_id=msg.from_user.id)
    question_id = add_question_to_poll(poll_id, data['question_text'], data['question_type'] == 'open')

    if data['question_type'] == 'closed':
        for option in data['options']:
            add_option_to_question(question_id, option)

    await msg.answer(f"Опрос создан! ID: {poll_id}")
    await state.clear()