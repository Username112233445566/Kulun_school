import logging
from services.google_sheets import GoogleSheetsManager

logger = logging.getLogger(__name__)


def initialize_system():
    """Инициализация системы БЕЗ автоматической синхронизации"""
    logger.info("🔄 Инициализация системы...")

    sheets_manager = GoogleSheetsManager()

    # Только создаем необходимые листы если их нет, но НЕ синхронизируем данные
    sheets_manager.get_worksheet("Users")
    sheets_manager.get_worksheet("Groups")
    sheets_manager.get_worksheet("Assignments")
    sheets_manager.get_worksheet("Attendance")

    logger.info("✅ Система инициализирована (листы готовы, синхронизация отключена)")