# utils/auto_sync.py
import logging
from services.sync_manager import SyncManager

logger = logging.getLogger(__name__)


def initialize_system():
    """Инициализация системы с автоматической синхронизацией"""
    logger.info("🔄 Инициализация системы...")

    sync_manager = SyncManager()

    # Создаем необходимые листы если их нет
    sync_manager.sheets.get_worksheet("Users")
    sync_manager.sheets.get_worksheet("Groups")
    sync_manager.sheets.get_worksheet("Assignments")
    sync_manager.sheets.get_worksheet("Attendance")

    # Первоначальная синхронизация
    sync_manager.full_sync()

    logger.info("✅ Система инициализирована и синхронизирована")