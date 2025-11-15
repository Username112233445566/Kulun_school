import os
from dotenv import load_dotenv

load_dotenv()

# Настройки бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Настройки Google Sheets
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
CREDENTIALS_FILE = "credentials.json"

# Названия листов в Google Sheets
SHEET_NAMES = {
    "users": "Users",
    "groups": "Groups",
    "assignments": "Assignments",
    "attendance": "Attendance"
}

# Роли пользователей
ROLES = {
    "student": "🎒 Ученик",
    "teacher": "👨‍🏫 Учитель",
    "admin": "⚙️ Администратор"
}