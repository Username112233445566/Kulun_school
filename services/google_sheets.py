# services/google_sheets.py
import gspread
from google.oauth2.service_account import Credentials
from config.config import SPREADSHEET_ID, CREDENTIALS_FILE
import logging
import time

logger = logging.getLogger(__name__)


class GoogleSheetsManager:
    def __init__(self):
        self.scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        try:
            self.creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=self.scope)
            self.client = gspread.authorize(self.creds)
            self.sheet = self.client.open_by_key(SPREADSHEET_ID)
            logger.info("✅ Google Sheets подключен")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Google Sheets: {e}")
            self.client = None

    def get_worksheet(self, sheet_name):
        """Получить лист с обработкой ошибок"""
        if not self.client:
            return None

        try:
            # Пробуем получить существующий лист
            return self.sheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            try:
                # Создаем новый лист
                worksheet = self.sheet.add_worksheet(title=sheet_name, rows=1000, cols=20)

                # Добавляем заголовки для основных листов
                if sheet_name == "Users":
                    worksheet.append_row([
                        "ID", "Telegram ID", "Full Name", "Phone", "Role",
                        "Status", "Group ID", "Group Name", "Created At"
                    ])
                elif sheet_name == "Groups":
                    worksheet.append_row([
                        "ID", "Name", "Teacher ID", "Teacher Name",
                        "Students Count", "Created At"
                    ])
                elif sheet_name == "Assignments":
                    worksheet.append_row([
                        "ID", "Title", "Description", "Group ID", "Group Name",
                        "Teacher ID", "Teacher Name", "Deadline", "Created At"
                    ])
                elif sheet_name == "Attendance":
                    worksheet.append_row([
                        "ID", "Date", "Group ID", "Group Name", "Student ID",
                        "Student Name", "Status", "Marked By", "Marked At"
                    ])

                logger.info(f"✅ Создан новый лист: {sheet_name}")
                return worksheet
            except Exception as e:
                logger.error(f"❌ Ошибка создания листа {sheet_name}: {e}")
                return None
        except Exception as e:
            logger.error(f"❌ Ошибка доступа к листу {sheet_name}: {e}")
            return None

    def safe_append_row(self, worksheet, row_data):
        """Безопасное добавление строки с повторными попытками"""
        if not worksheet:
            return False

        max_retries = 3
        for attempt in range(max_retries):
            try:
                worksheet.append_row(row_data)
                return True
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1)  # Ждем секунду перед повторной попыткой
                    continue
                logger.error(f"❌ Ошибка добавления строки после {max_retries} попыток: {e}")
                return False

    def safe_update_cell(self, worksheet, row, col, value):
        """Безопасное обновление ячейки с повторными попытками"""
        if not worksheet:
            return False

        max_retries = 3
        for attempt in range(max_retries):
            try:
                worksheet.update_cell(row, col, value)
                return True
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                logger.error(f"❌ Ошибка обновления ячейки после {max_retries} попыток: {e}")
                return False