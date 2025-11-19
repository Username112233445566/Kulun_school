import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
CREDENTIALS_FILE = "credentials.json"

SHEET_NAMES = {
    "users": "Users",
    "groups": "Groups",
    "assignments": "Assignments",
    "attendance": "Attendance"
}

ROLES = {
    "student": "Ученик",
    "teacher": "Учитель",
    "admin": "Администратор"
}