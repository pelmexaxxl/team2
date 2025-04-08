from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
import asyncio
import logging

from config import TOKEN
from handlers import admin  # подключай другие модули, если появятся

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(admin.router)

    # Команды бота
    await bot.set_my_commands([
        BotCommand(command="create_poll", description="Создать новый опрос"),
    ])

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
