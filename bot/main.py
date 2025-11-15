# bot/main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from config.config import BOT_TOKEN
from bot.handlers import common, student, teacher, admin

# ОПТИМИЗАЦИЯ ЛОГИРОВАНИЯ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
# Убираем лишние логи
logging.getLogger('aiogram').setLevel(logging.WARNING)
logging.getLogger('gspread').setLevel(logging.WARNING)
logging.getLogger('google').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# bot/main.py - ОБНОВЛЕННАЯ ФУНКЦИЯ MAIN
async def main():
    logger.info("🚀 Запуск ОПТИМИЗИРОВАННОГО бота KULUN School...")

    try:
        # ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ
        from utils.auto_sync import initialize_system
        initialize_system()

        # ОПТИМИЗИРОВАННЫЙ БОТ
        bot = Bot(
            token=BOT_TOKEN,
            default=DefaultBotProperties(
                parse_mode="HTML",
                link_preview_is_disabled=True
            )
        )

        dp = Dispatcher(storage=MemoryStorage())

        # Регистрируем роутеры
        dp.include_router(common.router)
        dp.include_router(student.router)
        dp.include_router(teacher.router)
        dp.include_router(admin.router)

        logger.info("✅ Бот оптимизирован и готов к работе")

        # ОЧИСТКА ОЧЕРЕДИ ДЛЯ БЫСТРОГО СТАРТА
        await bot.delete_webhook(drop_pending_updates=True)

        # ЗАПУСКАЕМ ПОЛЛИНГ
        await dp.start_polling(bot)

    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())