from aiogram import Bot
from db import get_users_in_chat

async def send_poll_to_users(bot: Bot, chat_id: int, poll_id: int):
    users = get_users_in_chat(chat_id)
    for user in users:
        try:
            await bot.send_message(
                user['id'],
                f"Вы приглашены пройти опрос #{poll_id}! Перейдите в бот, чтобы пройти его."
            )
        except Exception as e:
            print(f"❌ Не удалось отправить сообщение {user['id']}: {e}")