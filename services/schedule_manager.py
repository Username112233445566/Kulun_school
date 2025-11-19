import logging
from typing import List, Dict, Optional
from .database import Database

logger = logging.getLogger(__name__)

class ScheduleManager:
    def __init__(self):
        self.db = Database()

    def add_schedule_item(self, group_id: int, day_of_week: str, start_time: str,
                          end_time: str, subject: str, teacher_id: int = None) -> bool:
        try:
            if not all([group_id, day_of_week, start_time, end_time, subject]):
                logger.error(f"Missing data for schedule: group_id={group_id}, day={day_of_week}")
                return False

            self.db.execute(
                """INSERT INTO schedule (group_id, day_of_week, start_time, end_time, subject, teacher_id)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (group_id, day_of_week, start_time, end_time, subject, teacher_id)
            )
            logger.info(f"Schedule item added for group {group_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding schedule: {e}")
            return False

    def get_group_schedule(self, group_id: int) -> List[Dict]:
        try:
            return self.db.fetch_all(
                """SELECT s.*, u.full_name as teacher_name
                   FROM schedule s
                   LEFT JOIN users u ON s.teacher_id = u.id
                   WHERE s.group_id = ?
                   ORDER BY 
                     CASE s.day_of_week
                       WHEN 'monday' THEN 1
                       WHEN 'tuesday' THEN 2
                       WHEN 'wednesday' THEN 3
                       WHEN 'thursday' THEN 4
                       WHEN 'friday' THEN 5
                       WHEN 'saturday' THEN 6
                       WHEN 'sunday' THEN 7
                     END,
                     s.start_time""",
                (group_id,)
            )
        except Exception as e:
            logger.error(f"Error getting schedule: {e}")
            return []

    def delete_schedule_item(self, schedule_id: int) -> bool:
        try:
            self.db.execute("DELETE FROM schedule WHERE id = ?", (schedule_id,))
            logger.info(f"Schedule item {schedule_id} deleted")
            return True
        except Exception as e:
            logger.error(f"Error deleting schedule: {e}")
            return False

    def get_schedule_by_day(self, group_id: int, day_of_week: str) -> List[Dict]:
        try:
            return self.db.fetch_all(
                """SELECT s.*, u.full_name as teacher_name
                   FROM schedule s
                   LEFT JOIN users u ON s.teacher_id = u.id
                   WHERE s.group_id = ? AND s.day_of_week = ?
                   ORDER BY s.start_time""",
                (group_id, day_of_week)
            )
        except Exception as e:
            logger.error(f"Error getting daily schedule: {e}")
            return []