import logging
from datetime import datetime

from . import UserManager
from .database import Database

logger = logging.getLogger(__name__)


class AssignmentManager:
    def __init__(self):
        self.db = Database()

    def create_assignment(self, title: str, description: str, group_id: int, teacher_id: int,
                          deadline: datetime.date) -> int:
        """Создать новое задание"""
        try:
            cursor = self.db.execute(
                """INSERT INTO assignments (title, description, group_id, teacher_id, deadline)
                   VALUES (?, ?, ?, ?, ?)""",
                (title, description, group_id, teacher_id, deadline)
            )

            assignment_id = cursor.lastrowid
            logger.info(f"✅ Задание создано: {title} для группы {group_id}")
            return assignment_id
        except Exception as e:
            logger.error(f"❌ Ошибка при создании задания: {e}")
            return None

    def get_assignments_for_group(self, group_id: int) -> list:
        """Получить задания для группы"""
        return self.db.fetch_all(
            """SELECT a.*, u.full_name as teacher_name
               FROM assignments a
                        JOIN users u ON a.teacher_id = u.id
               WHERE a.group_id = ?
               ORDER BY a.deadline ASC""",
            (group_id,)
        )

    def get_teacher_assignments(self, teacher_id: int) -> list:
        """Получить задания учителя"""
        return self.db.fetch_all(
            """SELECT a.*, g.name as group_name
               FROM assignments a
                        JOIN groups g ON a.group_id = g.id
               WHERE a.teacher_id = ?
               ORDER BY a.deadline ASC""",
            (teacher_id,)
        )

    def delete_assignment(self, assignment_id: int, teacher_id: int) -> bool:
        """Удалить задание (только создавший учитель)"""
        try:
            # Проверяем, что задание создано этим учителем
            assignment = self.db.fetch_one(
                "SELECT id FROM assignments WHERE id = ? AND teacher_id = ?",
                (assignment_id, teacher_id)
            )

            if not assignment:
                return False

            self.db.execute(
                "DELETE FROM assignments WHERE id = ?",
                (assignment_id,)
            )

            logger.info(f"✅ Задание {assignment_id} удалено")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при удалении задания: {e}")
            return False

    # services/assignment_manager.py - ИСПРАВЛЕННЫЙ МЕТОД
    def get_assignments_for_student(self, student_id: int) -> list:
        """Получить задания для конкретного ученика"""
        try:
            # Получаем ученика и его группу
            user_manager = UserManager()
            student = user_manager.get_user_by_id(student_id)

            if not student or not student.get('group_id'):
                return []

            # Получаем задания для группы ученика
            return self.db.fetch_all(
                """SELECT a.*, u.full_name as teacher_name, g.name as group_name
                   FROM assignments a
                            JOIN users u ON a.teacher_id = u.id
                            JOIN groups g ON a.group_id = g.id
                   WHERE a.group_id = ?
                   ORDER BY a.deadline ASC""",
                (student['group_id'],)
            )
        except Exception as e:
            logger.error(f"❌ Ошибка при получении заданий для ученика: {e}")
            return []