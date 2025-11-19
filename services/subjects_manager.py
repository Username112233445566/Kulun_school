import logging
from typing import List, Dict, Optional
from .database import Database

logger = logging.getLogger(__name__)

class SubjectsManager:
    def __init__(self):
        self.db = Database()

    def add_subject(self, name: str, description: str = None) -> bool:
        try:
            self.db.execute("INSERT INTO subjects (name, description) VALUES (?, ?)", (name, description))
            logger.info(f"Subject '{name}' added")
            return True
        except Exception as e:
            logger.error(f"Error adding subject: {e}")
            return False

    def get_all_subjects(self) -> List[Dict]:
        try:
            return self.db.fetch_all("SELECT * FROM subjects ORDER BY name")
        except Exception as e:
            logger.error(f"Error getting subjects: {e}")
            return []

    def get_subject(self, subject_id: int) -> Optional[Dict]:
        try:
            return self.db.fetch_one("SELECT * FROM subjects WHERE id = ?", (subject_id,))
        except Exception as e:
            logger.error(f"Error getting subject: {e}")
            return None

    def delete_subject(self, subject_id: int) -> bool:
        try:
            self.db.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
            logger.info(f"Subject {subject_id} deleted")
            return True
        except Exception as e:
            logger.error(f"Error deleting subject: {e}")
            return False

    def update_subject(self, subject_id: int, name: str, description: str = None) -> bool:
        try:
            self.db.execute("UPDATE subjects SET name = ?, description = ? WHERE id = ?", (name, description, subject_id))
            logger.info(f"Subject {subject_id} updated")
            return True
        except Exception as e:
            logger.error(f"Error updating subject: {e}")
            return False