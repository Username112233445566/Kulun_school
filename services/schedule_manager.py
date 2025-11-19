import logging
from typing import List, Dict, Optional
from .database import Database

logger = logging.getLogger(__name__)

class ScheduleManager:
    def __init__(self):
        self.db = Database()

    def add_schedule_item(self, group_id: int, day_of_week: str, start_time: str,
                          end_time: str, subject: str, teacher_id: int = None) -> bool:
        """Добавить элемент расписания"""
        try:
            # ДОБАВЬТЕ ПРОВЕРКУ ДАННЫХ
            if not all([group_id, day_of_week, start_time, end_time, subject]):
                logger.error(f"❌ Не все данные переданы для создания расписания: "
                             f"group_id={group_id}, day={day_of_week}, time={start_time}-{end_time}, subject={subject}")
                return False

            self.db.execute(
                """INSERT INTO schedule (group_id, day_of_week, start_time, end_time, subject, teacher_id)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (group_id, day_of_week, start_time, end_time, subject, teacher_id)
            )
            logger.info(f"✅ Элемент расписания добавлен для группы {group_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при добавлении расписания: {e}")
            return False

    def get_group_schedule(self, group_id: int) -> List[Dict]:
        """Получить расписание группы"""
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
            logger.error(f"❌ Ошибка при получении расписания: {e}")
            return []

    def delete_schedule_item(self, schedule_id: int) -> bool:
        """Удалить элемент расписания"""
        try:
            self.db.execute(
                "DELETE FROM schedule WHERE id = ?",
                (schedule_id,)
            )
            logger.info(f"✅ Элемент расписания {schedule_id} удален")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при удалении расписания: {e}")
            return False

    def get_schedule_by_day(self, group_id: int, day_of_week: str) -> List[Dict]:
        """Получить расписание группы на конкретный день"""
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
            logger.error(f"❌ Ошибка при получении расписания на день: {e}")
            return []