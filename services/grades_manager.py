import logging
from datetime import datetime
from typing import List, Dict, Optional
from .database import Database

logger = logging.getLogger(__name__)

class GradesManager:
    def __init__(self):
        self.db = Database()

    def add_grade(self, student_id: int, group_id: int, subject: str, grade: int,
                  teacher_id: int, date: datetime.date = None, comment: str = None) -> bool:
        try:
            if date is None:
                date = datetime.now().date()

            if grade < 1 or grade > 5:
                logger.error(f"Invalid grade: {grade}")
                return False

            self.db.execute(
                """INSERT INTO grades (student_id, group_id, subject, grade, date, teacher_id, comment)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (student_id, group_id, subject, grade, date, teacher_id, comment)
            )
            logger.info(f"Grade {grade} added for student {student_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding grade: {e}")
            return False

    def get_student_grades(self, student_id: int, subject: str = None) -> List[Dict]:
        try:
            if subject:
                return self.db.fetch_all(
                    "SELECT * FROM grades WHERE student_id = ? AND subject = ? ORDER BY date DESC",
                    (student_id, subject)
                )
            else:
                return self.db.fetch_all(
                    "SELECT * FROM grades WHERE student_id = ? ORDER BY date DESC",
                    (student_id,)
                )
        except Exception as e:
            logger.error(f"Error getting student grades: {e}")
            return []

    def get_group_grades(self, group_id: int, subject: str = None) -> List[Dict]:
        try:
            if subject:
                return self.db.fetch_all(
                    """SELECT g.*, u.full_name as student_name
                       FROM grades g
                       JOIN users u ON g.student_id = u.id
                       WHERE g.group_id = ? AND g.subject = ?
                       ORDER BY g.date DESC""",
                    (group_id, subject)
                )
            else:
                return self.db.fetch_all(
                    """SELECT g.*, u.full_name as student_name
                       FROM grades g
                       JOIN users u ON g.student_id = u.id
                       WHERE g.group_id = ?
                       ORDER BY g.date DESC""",
                    (group_id,)
                )
        except Exception as e:
            logger.error(f"Error getting group grades: {e}")
            return []

    def get_average_grade(self, student_id: int, subject: str = None) -> float:
        try:
            if subject:
                result = self.db.fetch_one(
                    "SELECT AVG(grade) as average FROM grades WHERE student_id = ? AND subject = ?",
                    (student_id, subject)
                )
            else:
                result = self.db.fetch_one(
                    "SELECT AVG(grade) as average FROM grades WHERE student_id = ?",
                    (student_id,)
                )

            return round(result['average'], 2) if result and result['average'] is not None else 0.0
        except Exception as e:
            logger.error(f"Error calculating average grade: {e}")
            return 0.0

    def get_group_average_grade(self, group_id: int, subject: str = None) -> float:
        try:
            if subject:
                result = self.db.fetch_one(
                    "SELECT AVG(grade) as average FROM grades WHERE group_id = ? AND subject = ?",
                    (group_id, subject)
                )
            else:
                result = self.db.fetch_one(
                    "SELECT AVG(grade) as average FROM grades WHERE group_id = ?",
                    (group_id,)
                )

            return round(result['average'], 2) if result and result['average'] is not None else 0.0
        except Exception as e:
            logger.error(f"Error calculating group average grade: {e}")
            return 0.0

    def get_recent_grades(self, group_id: int, limit: int = 10) -> List[Dict]:
        try:
            return self.db.fetch_all(
                """SELECT g.*, u.full_name as student_name
                   FROM grades g
                   JOIN users u ON g.student_id = u.id
                   WHERE g.group_id = ?
                   ORDER BY g.created_at DESC LIMIT ?""",
                (group_id, limit)
            )
        except Exception as e:
            logger.error(f"Error getting recent grades: {e}")
            return []

    def get_grade_statistics(self, group_id: int) -> Dict:
        try:
            total_grades = self.db.fetch_one(
                "SELECT COUNT(*) as count FROM grades WHERE group_id = ?",
                (group_id,)
            )['count']

            grade_distribution = self.db.fetch_all(
                "SELECT grade, COUNT(*) as count FROM grades WHERE group_id = ? GROUP BY grade ORDER BY grade",
                (group_id,)
            )

            average_grade = self.get_group_average_grade(group_id)

            return {
                'total_grades': total_grades,
                'average_grade': average_grade,
                'grade_distribution': {item['grade']: item['count'] for item in grade_distribution}
            }
        except Exception as e:
            logger.error(f"Error getting grade statistics: {e}")
            return {'total_grades': 0, 'average_grade': 0.0, 'grade_distribution': {}}