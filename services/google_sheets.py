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
            logger.info("Google Sheets connected")
        except Exception as e:
            logger.error(f"Error connecting to Google Sheets: {e}")
            self.client = None

    def get_worksheet(self, sheet_name):
        if not self.client:
            return None

        try:
            return self.sheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            try:
                worksheet = self.sheet.add_worksheet(title=sheet_name, rows=1000, cols=20)

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

                logger.info(f"New sheet created: {sheet_name}")
                return worksheet
            except Exception as e:
                logger.error(f"Error creating sheet {sheet_name}: {e}")
                return None
        except Exception as e:
            logger.error(f"Error accessing sheet {sheet_name}: {e}")
            return None

    def safe_append_row(self, worksheet, row_data):
        if not worksheet:
            return False

        max_retries = 3
        for attempt in range(max_retries):
            try:
                worksheet.append_row(row_data)
                return True
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                logger.error(f"Error adding row after {max_retries} attempts: {e}")
                return False

    def safe_update_cell(self, worksheet, row, col, value):
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
                logger.error(f"Error updating cell after {max_retries} attempts: {e}")
                return False

    def clear_worksheet(self, worksheet):
        if not worksheet:
            return False

        try:
            worksheet.clear()
            return True
        except Exception as e:
            logger.error(f"Error clearing sheet: {e}")
            return False

    def get_all_records_safe(self, worksheet):
        if not worksheet:
            return []

        try:
            return worksheet.get_all_records()
        except Exception as e:
            logger.error(f"Error getting records: {e}")
            return []