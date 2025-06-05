from aiogram import Router, F
from aiogram.types import Message, ChatMemberUpdated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from app.models.extras import ChatSettings

router = Router(name="welcome_router")

@router.message(F.text.startswith("/set_welcome"))
async def set_welcome(msg: Message, session: AsyncSession):
    if msg.chat.type == "private":
        await msg.answer("Команда работает только в группах.")
        return
    text = msg.text.partition(" ")[2].strip()
    if not text:
        await msg.answer("После команды укажите текст приветствия.")
        return
    await session.execute(
        insert(ChatSettings)
        .values(chat_id=msg.chat.id, welcome_text=text)
        .on_conflict_do_update(
            index_elements=[ChatSettings.chat_id],
            set_={"welcome_text": text}
        )
    )
    await session.commit()
    await msg.answer("✅ Приветствие сохранено!")

@router.chat_member()                               # ловим join
async def greet(ev: ChatMemberUpdated, session: AsyncSession):
    if ev.new_chat_member.user.is_bot:               # игнорируем ботов
        return
    row = await session.scalar(select(ChatSettings.welcome_text)
                               .where(ChatSettings.chat_id == ev.chat.id))
    if row:
        await ev.bot.send_message(ev.chat.id, row.replace("{user}", ev.new_chat_member.user.get_mention()))
