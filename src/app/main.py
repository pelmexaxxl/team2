from aiogram import Bot, Dispatcher

from app.configs import settings
from app.handlers.user import router as user_router
from app.handlers.admin import router as admin_router
from app.middlewares.db import DatabaseMiddleware

bot = Bot(settings.BOT_TOKEN)
dp = Dispatcher()
dp.message.middleware(DatabaseMiddleware())
dp.include_router(user_router)
dp.include_router(admin_router)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("/app/logs/bot_log.log", mode='a', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    import asyncio
    asyncio.run(main())
