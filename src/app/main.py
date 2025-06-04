from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import logging

from app.handlers import analyze
from app.configs import settings
from app.handlers.user import router as user_router
from app.handlers.admin import router as admin_router
from app.handlers.message_collector import router as collector_router
# 🆕 новые роутеры
from app.handlers.welcome import router as welcome_router
from app.handlers.cabinet import router as cabinet_router
from app.handlers.plots import router as plots_router

# 🆕 фоновые задачи
from app.services.reminders import check_and_send
from app.services.summary    import send_daily_summary

# фабрика сессий
from app.db.db import async_session_maker

from app.middlewares.db import DatabaseMiddleware
from app.services.analytics import run_daily_analysis
from aiogram.fsm.storage.memory import MemoryStorage


logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(settings.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Middleware
db_mw = DatabaseMiddleware()
dp.message.middleware(db_mw)
dp.callback_query.middleware(db_mw)

# Регистрация обработчиков с приоритетами
# Команды имеют более высокий приоритет
user_router.message.filter(lambda msg: msg.text and msg.text.startswith("/"))
admin_router.message.filter(lambda msg: msg.text and msg.text.startswith("/"))
# Для анализа не устанавливаем фильтр по команде, так как нам нужны и обычные сообщения для FSM

# Важен порядок подключения роутеров!
# 1. Сначала специальные обработчики для команд
dp.include_router(user_router)
dp.include_router(admin_router)
dp.include_router(analyze.router)
dp.include_router(welcome_router)
dp.include_router(cabinet_router)
dp.include_router(plots_router)

# 2. Самым последним должен быть обработчик сообщений,
#    чтобы он не перехватывал команды из других роутеров
dp.include_router(collector_router)

# Функция запуска бота
async def main():
    try:
        # Проверка настроек
        logger.info("Bot configuration:")
        logger.info(f"- BOT_TOKEN: {'configured' if settings.BOT_TOKEN else 'missing'}")
        logger.info(f"- DATABASE_URL: {settings.database_url}")
        logger.info(f"- ADMIN_USER_ID: {settings.ADMIN_USER_ID}")
        
        # Проверка порядка обработчиков
        logger.info("Registered handlers in order of priority:")
        for i, router in enumerate([user_router, admin_router, analyze.router, collector_router]):
            logger.info(f"{i+1}. {router.name if hasattr(router, 'name') else 'unnamed router'}")
        
        # Start the daily analysis task
        daily_task = asyncio.create_task(run_daily_analysis())
        logger.info("Daily analysis task scheduled")
        # ----------------  APScheduler  ----------------
        scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
        # напоминания раз в 6 часов
        scheduler.add_job(check_and_send,
                          "interval", hours=6,
                          args=[bot, async_session_maker])
        # ежедневная HR-сводка в 18:00
        scheduler.add_job(send_daily_summary,
                          "cron", hour=18, minute=0,
                          args=[bot, async_session_maker])
        # если хотите, перенесите run_daily_analysis в планировщик:
        scheduler.add_job(run_daily_analysis, "cron", hour=2)

        scheduler.start()
        logger.info("Scheduler started with 3 jobs")
        
        # ----------------  Запуск бота  ----------------
        logger.info("Bot started, listening for messages...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise


if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("/app/logs/bot_log.log", mode='a', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # Запуск бота
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}", exc_info=True)
