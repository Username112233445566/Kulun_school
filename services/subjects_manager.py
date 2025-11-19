import logging
from typing import List, Dict, Optional
from .database import Database

logger = logging.getLogger(__name__)

class SubjectsManager:
    def __init__(self):
        self.db = Database()

    def add_subject(self, name: str, description: str = None) -> bool:
        """Добавить новый предмет"""
        try:
            self.db.execute(
                "INSERT INTO subjects (name, description) VALUES (?, ?)",
                (name, description)
            )
            logger.info(f"✅ Предмет '{name}' добавлен")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при добавлении предмета: {e}")
            return False

    def get_all_subjects(self) -> List[Dict]:
        """Получить все предметы"""
        try:
            return self.db.fetch_all("SELECT * FROM subjects ORDER BY name")
        except Exception as e:
            logger.error(f"❌ Ошибка при получении предметов: {e}")
            return []

    def get_subject(self, subject_id: int) -> Optional[Dict]:
        """Получить предмет по ID"""
        try:
            return self.db.fetch_one("SELECT * FROM subjects WHERE id = ?", (subject_id,))
        except Exception as e:
            logger.error(f"❌ Ошибка при получении предмета: {e}")
            return None

    def delete_subject(self, subject_id: int) -> bool:
        """Удалить предмет"""
        try:
            self.db.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
            logger.info(f"✅ Предмет {subject_id} удален")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при удалении предмета: {e}")
            return False

    def update_subject(self, subject_id: int, name: str, description: str = None) -> bool:
        """Обновить предмет"""
        try:
            self.db.execute(
                "UPDATE subjects SET name = ?, description = ? WHERE id = ?",
                (name, description, subject_id)
            )
            logger.info(f"✅ Предмет {subject_id} обновлен")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при обновлении предмета: {e}")
            return False