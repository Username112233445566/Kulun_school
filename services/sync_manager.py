import logging
from typing import List, Dict
from .database import Database
from .google_sheets import GoogleSheetsManager
from datetime import datetime

logger = logging.getLogger(__name__)

class SyncManager:
    def __init__(self):
        self.db = Database()
        self.sheets = GoogleSheetsManager()

    def sync_users_to_sheets(self):
        try:
            users = self.db.fetch_all("SELECT * FROM users")
            worksheet = self.sheets.get_worksheet("Users")

            if not worksheet:
                logger.error("Cannot get Users worksheet")
                return False

            worksheet.clear()
            worksheet.append_row([
                "ID", "Telegram ID", "Full Name", "Phone", "Role",
                "Status", "Group ID", "Group Name", "Created At"
            ])

            for user in users:
                group_name = ""
                if user.get('group_id'):
                    group = self.db.fetch_one("SELECT name FROM groups WHERE id = ?", (user['group_id'],))
                    group_name = group['name'] if group else ""

                self.sheets.safe_append_row(worksheet, [
                    user['id'],
                    user['telegram_id'],
                    user['full_name'],
                    user['phone'],
                    user['role'],
                    user['status'],
                    user.get('group_id', ''),
                    group_name,
                    user['created_at']
                ])

            logger.info("Users synced to Google Sheets")
            return True
        except Exception as e:
            logger.error(f"Error syncing users: {e}")
            return False

    def sync_groups_to_sheets(self):
        try:
            groups = self.db.fetch_all("""
                SELECT g.*, u.full_name as teacher_name
                FROM groups g
                LEFT JOIN users u ON g.teacher_id = u.id
            """)
            worksheet = self.sheets.get_worksheet("Groups")

            if not worksheet:
                logger.error("Cannot get Groups worksheet")
                return False

            worksheet.clear()
            worksheet.append_row([
                "ID", "Name", "Teacher ID", "Teacher Name",
                "Students Count", "Created At"
            ])

            for group in groups:
                students_count = self.db.fetch_one(
                    "SELECT COUNT(*) as count FROM users WHERE group_id = ? AND role = 'student' AND status = 'active'",
                    (group['id'],)
                )
                students_count = students_count['count'] if students_count else 0

                self.sheets.safe_append_row(worksheet, [
                    group['id'],
                    group['name'],
                    group.get('teacher_id', ''),
                    group.get('teacher_name', ''),
                    students_count,
                    group['created_at']
                ])

            logger.info("Groups synced to Google Sheets")
            return True
        except Exception as e:
            logger.error(f"Error syncing groups: {e}")
            return False

    def sync_from_sheets(self):
        try:
            groups_worksheet = self.sheets.get_worksheet("Groups")
            if groups_worksheet:
                groups_data = groups_worksheet.get_all_records()

                for group_row in groups_data:
                    if group_row.get('ID') and group_row.get('Name'):
                        existing_group = self.db.fetch_one(
                            "SELECT * FROM groups WHERE id = ? OR name = ?",
                            (group_row['ID'], group_row['Name'])
                        )

                        if existing_group:
                            self.db.execute(
                                "UPDATE groups SET name = ?, teacher_id = ? WHERE id = ?",
                                (group_row['Name'], group_row.get('Teacher ID'), existing_group['id'])
                            )
                        else:
                            self.db.execute(
                                "INSERT INTO groups (name, teacher_id) VALUES (?, ?)",
                                (group_row['Name'], group_row.get('Teacher ID'))
                            )

            users_worksheet = self.sheets.get_worksheet("Users")
            if users_worksheet:
                users_data = users_worksheet.get_all_records()

                for user_row in users_data:
                    if user_row.get('Telegram ID') and user_row.get('Full Name'):
                        existing_user = self.db.fetch_one(
                            "SELECT * FROM users WHERE telegram_id = ?",
                            (user_row['Telegram ID'],)
                        )

                        group_id = None
                        if user_row.get('Group ID'):
                            group_id = user_row['Group ID']
                        elif user_row.get('Group Name'):
                            group = self.db.fetch_one("SELECT id FROM groups WHERE name = ?", (user_row['Group Name'],))
                            group_id = group['id'] if group else None

                        if existing_user:
                            self.db.execute(
                                """UPDATE users
                                   SET full_name = ?, phone = ?, role = ?, status = ?, group_id = ?
                                   WHERE telegram_id = ?""",
                                (
                                    user_row['Full Name'], user_row['Phone'], user_row['Role'],
                                    user_row.get('Status', 'pending'), group_id, user_row['Telegram ID']
                                )
                            )
                        else:
                            self.db.execute(
                                """INSERT INTO users (telegram_id, full_name, phone, role, status, group_id, created_at)
                                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                                (
                                    user_row['Telegram ID'], user_row['Full Name'], user_row['Phone'],
                                    user_row['Role'], user_row.get('Status', 'pending'), group_id,
                                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                )
                            )

            logger.info("Data synced from Google Sheets")
            return True
        except Exception as e:
            logger.error(f"Error syncing from Google Sheets: {e}")
            return False

    def full_sync(self):
        logger.info("Starting full sync...")

        users_success = self.sync_users_to_sheets()
        groups_success = self.sync_groups_to_sheets()

        if users_success and groups_success:
            logger.info("Full sync completed")
            return True
        else:
            logger.error("Full sync completed with errors")
            return False