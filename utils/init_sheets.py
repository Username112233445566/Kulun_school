from services.google_sheets import GoogleSheetsManager


def initialize_google_sheets():
    """Инициализирует Google Sheets с нужной структурой"""
    sheets_manager = GoogleSheetsManager()

    # Просто пытаемся получить листы - они создадутся автоматически
    sheets_manager.get_worksheet("Users")
    sheets_manager.get_worksheet("Groups")
    sheets_manager.get_worksheet("Assignments")
    sheets_manager.get_worksheet("Attendance")

    print("✅ Google Sheets инициализированы")


if __name__ == "__main__":
    initialize_google_sheets()