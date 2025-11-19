import logging
from datetime import datetime
from .database import Database

logger = logging.getLogger(__name__)

class AttendanceManager:
    def __init__(self):
        self.db = Database()

    def mark_attendance(self, student_id: int, group_id: int, date: datetime.date, status: str, marked_by: int) -> bool:
        try:
            existing = self.db.fetch_one(
                "SELECT id FROM attendance WHERE student_id = ? AND date = ? AND group_id = ?",
                (student_id, date, group_id)
            )

            if existing:
                self.db.execute(
                    "UPDATE attendance SET status = ?, marked_by = ?, marked_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (status, marked_by, existing['id'])
                )
            else:
                self.db.execute(
                    """INSERT INTO attendance (date, group_id, student_id, status, marked_by)
                       VALUES (?, ?, ?, ?, ?)""",
                    (date, group_id, student_id, status, marked_by)
                )
            return True
        except Exception as e:
            logger.error(f"Error marking attendance: {e}")
            return False

    def get_group_attendance(self, group_id: int, date: datetime.date) -> list:
        try:
            return self.db.fetch_all(
                """SELECT u.full_name, a.status
                   FROM attendance a
                   JOIN users u ON a.student_id = u.id
                   WHERE a.group_id = ? AND a.date = ?""",
                (group_id, date)
            )
        except Exception as e:
            logger.error(f"Error getting attendance: {e}")
            return []

    def get_student_attendance_stats(self, student_id: int, group_id: int) -> dict:
        try:
            total = self.db.fetch_one(
                "SELECT COUNT(*) as total FROM attendance WHERE student_id = ? AND group_id = ?",
                (student_id, group_id)
            )
            total = total['total'] if total else 0

            present = self.db.fetch_one(
                "SELECT COUNT(*) as present FROM attendance WHERE student_id = ? AND group_id = ? AND status = 'present'",
                (student_id, group_id)
            )
            present = present['present'] if present else 0

            return {
                'total_classes': total,
                'present': present,
                'attendance_rate': round((present / total) * 100, 2) if total > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting attendance stats: {e}")
            return {'total_classes': 0, 'present': 0, 'attendance_rate': 0}