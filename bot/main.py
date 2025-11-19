import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from config.config import BOT_TOKEN
from bot.handlers import common, student, teacher

from bot.handlers.admin_main import router as admin_main_router
from bot.handlers.admin_users import router as admin_users_router
from bot.handlers.admin_groups import router as admin_groups_router
from bot.handlers.admin_sync import router as admin_sync_router
from bot.handlers.admin_creation import router as admin_creation_router
from bot.handlers.unknown import router as unknown_router
from bot.handlers.admin_subjects import router as admin_subjects_router
from bot.handlers.admin_schedule import router as admin_schedule_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

logging.getLogger('aiogram').setLevel(logging.WARNING)
logging.getLogger('gspread').setLevel(logging.WARNING)
logging.getLogger('google').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

async def main():
    logger.info("Запуск бота KULUN School...")

    try:
        from utils.auto_sync import initialize_system
        initialize_system()

        bot = Bot(
            token=BOT_TOKEN,
            default=DefaultBotProperties(
                parse_mode="HTML",
                link_preview_is_disabled=True
            )
        )

        dp = Dispatcher(storage=MemoryStorage())

        dp.include_router(common.router)
        dp.include_router(student.router)
        dp.include_router(teacher.router)

        dp.include_router(admin_main_router)
        dp.include_router(admin_users_router)
        dp.include_router(admin_groups_router)
        dp.include_router(admin_sync_router)
        dp.include_router(admin_creation_router)
        dp.include_router(admin_subjects_router)
        dp.include_router(admin_schedule_router)

        logger.info("Бот готов к работе")

        await bot.delete_webhook(drop_pending_updates=True)

        await dp.start_polling(bot)

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())