import logging
from services.google_sheets import GoogleSheetsManager

logger = logging.getLogger(__name__)

def initialize_system():
    logger.info("Initializing system...")

    sheets_manager = GoogleSheetsManager()

    sheets_manager.get_worksheet("Users")
    sheets_manager.get_worksheet("Groups")
    sheets_manager.get_worksheet("Assignments")
    sheets_manager.get_worksheet("Attendance")

    logger.info("System initialized (sheets ready, sync disabled)")