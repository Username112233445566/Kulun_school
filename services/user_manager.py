import sqlite3
import logging
from typing import List, Dict, Optional
from .database import Database

logger = logging.getLogger(__name__)

class UserManager:
    def __init__(self):
        self.db = Database()
        self._ensure_admin_exists()

    def _ensure_admin_exists(self):
        admin_id = 1952805890

        admin = self.get_user(admin_id)
        if not admin:
            logger.info("Creating default admin...")
            success = self.create_user(
                telegram_id=admin_id,
                full_name="Администратор",
                phone="+79990000000",
                role="admin"
            )
            if success:
                self.db.execute("UPDATE users SET status = 'active' WHERE telegram_id = ?", (admin_id,))
                logger.info("Admin created")
            else:
                logger.error("Error creating admin")
        else:
            if admin['status'] != 'active':
                self.db.execute("UPDATE users SET status = 'active' WHERE telegram_id = ?", (admin_id,))
                logger.info("Admin activated")

    def create_user(self, telegram_id: int, full_name: str, phone: str, role: str) -> bool:
        try:
            self.db.execute(
                "INSERT INTO users (telegram_id, full_name, phone, role) VALUES (?, ?, ?, ?)",
                (telegram_id, full_name, phone, role)
            )
            logger.info(f"User {full_name} created")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"User {telegram_id} already exists")
            return False
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False

    def get_user(self, telegram_id: int) -> Optional[Dict]:
        return self.db.fetch_one("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        return self.db.fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))

    def approve_user(self, telegram_id: int) -> bool:
        try:
            self.db.execute("UPDATE users SET status = 'active' WHERE telegram_id = ?", (telegram_id,))
            logger.info(f"User {telegram_id} approved")
            return True
        except Exception as e:
            logger.error(f"Error approving user: {e}")
            return False

    def assign_user_to_group(self, user_id: int, group_id: int) -> bool:
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                logger.error(f"User with ID {user_id} not found")
                return False

            self.db.execute("UPDATE users SET group_id = ? WHERE id = ?", (group_id, user_id))
            logger.info(f"User {user['full_name']} assigned to group {group_id}")
            return True
        except Exception as e:
            logger.error(f"Error assigning user to group: {e}")
            return False

    def assign_teacher_to_group(self, teacher_id: int, group_id: int) -> bool:
        try:
            teacher = self.get_user_by_id(teacher_id)
            if not teacher:
                logger.error(f"Teacher with ID {teacher_id} not found")
                return False

            group = self.get_group(group_id)
            if not group:
                logger.error(f"Group with ID {group_id} not found")
                return False

            self.db.execute("UPDATE groups SET teacher_id = ? WHERE id = ?", (teacher_id, group_id))
            logger.info(f"Teacher {teacher['full_name']} assigned to group {group['name']}")
            return True
        except Exception as e:
            logger.error(f"Error assigning teacher to group: {e}")
            return False

    def update_group_teacher(self, group_id: int, teacher_id: int = None) -> bool:
        try:
            group = self.get_group(group_id)
            if not group:
                logger.error(f"Group with ID {group_id} not found")
                return False

            if teacher_id:
                teacher = self.get_user_by_id(teacher_id)
                if not teacher:
                    logger.error(f"Teacher with ID {teacher_id} not found")
                    return False

            self.db.execute("UPDATE groups SET teacher_id = ? WHERE id = ?", (teacher_id, group_id))
            action = "assigned" if teacher_id else "removed"
            logger.info(f"Teacher {action} for group {group['name']}")
            return True
        except Exception as e:
            logger.error(f"Error updating group teacher: {e}")
            return False

    def reject_user(self, telegram_id: int) -> bool:
        try:
            self.db.execute("UPDATE users SET status = 'rejected' WHERE telegram_id = ?", (telegram_id,))
            logger.info(f"User {telegram_id} rejected")
            return True
        except Exception as e:
            logger.error(f"Error rejecting user: {e}")
            return False

    def get_pending_users(self) -> List[Dict]:
        return self.db.fetch_all("SELECT * FROM users WHERE status = 'pending'")

    def create_group(self, name: str, teacher_id: int = None) -> bool:
        try:
            self.db.execute("INSERT INTO groups (name, teacher_id) VALUES (?, ?)", (name, teacher_id))
            logger.info(f"Group {name} created")
            return True
        except Exception as e:
            logger.error(f"Error creating group: {e}")
            return False

    def get_all_groups(self) -> List[Dict]:
        return self.db.fetch_all("SELECT * FROM groups")

    def get_group(self, group_id: int) -> Optional[Dict]:
        return self.db.fetch_one("SELECT * FROM groups WHERE id = ?", (group_id,))

    def get_group_with_details(self, group_id: int) -> Optional[Dict]:
        group = self.get_group(group_id)
        if not group:
            return None

        teacher = None
        if group.get('teacher_id'):
            teacher = self.get_user_by_id(group['teacher_id'])

        students = self.get_group_students(group_id)

        return {
            **group,
            'teacher': teacher,
            'students': students,
            'students_count': len(students)
        }

    def get_group_students(self, group_id: int) -> List[Dict]:
        return self.db.fetch_all(
            "SELECT * FROM users WHERE group_id = ? AND role = 'student' AND status = 'active'",
            (group_id,)
        )

    def get_students_without_groups(self) -> List[Dict]:
        return self.db.fetch_all(
            "SELECT * FROM users WHERE role = 'student' AND status = 'active' AND (group_id IS NULL OR group_id = '')"
        )

    def get_available_teachers(self) -> List[Dict]:
        return self.db.fetch_all("SELECT * FROM users WHERE role = 'teacher' AND status = 'active'")

    def get_active_students(self) -> List[Dict]:
        return self.db.fetch_all("SELECT * FROM users WHERE role = 'student' AND status = 'active'")

    def remove_student_from_group(self, student_id: int) -> bool:
        try:
            self.db.execute("UPDATE users SET group_id = NULL WHERE id = ?", (student_id,))
            logger.info(f"Student {student_id} removed from group")
            return True
        except Exception as e:
            logger.error(f"Error removing student from group: {e}")
            return False

    def delete_group(self, group_id: int) -> bool:
        try:
            self.db.execute("UPDATE users SET group_id = NULL WHERE group_id = ?", (group_id,))
            self.db.execute("DELETE FROM groups WHERE id = ?", (group_id,))
            logger.info(f"Group {group_id} deleted")
            return True
        except Exception as e:
            logger.error(f"Error deleting group: {e}")
            return False

    def update_group_name(self, group_id: int, new_name: str) -> bool:
        try:
            self.db.execute("UPDATE groups SET name = ? WHERE id = ?", (new_name, group_id))
            logger.info(f"Group {group_id} name changed to {new_name}")
            return True
        except Exception as e:
            logger.error(f"Error updating group name: {e}")
            return False

    def get_system_stats(self) -> Dict:
        total_users = self.db.fetch_one("SELECT COUNT(*) as count FROM users")['count']
        active_users = self.db.fetch_one("SELECT COUNT(*) as count FROM users WHERE status = 'active'")['count']
        pending_users = self.db.fetch_one("SELECT COUNT(*) as count FROM users WHERE status = 'pending'")['count']
        students_count = self.db.fetch_one("SELECT COUNT(*) as count FROM users WHERE role = 'student' AND status = 'active'")['count']
        teachers_count = self.db.fetch_one("SELECT COUNT(*) as count FROM users WHERE role = 'teacher' AND status = 'active'")['count']
        groups_count = self.db.fetch_one("SELECT COUNT(*) as count FROM groups")['count']

        return {
            'total_users': total_users,
            'active_users': active_users,
            'pending_users': pending_users,
            'students_count': students_count,
            'teachers_count': teachers_count,
            'groups_count': groups_count
        }

    def get_teacher_groups(self, teacher_id: int) -> List[Dict]:
        return self.db.fetch_all("SELECT * FROM groups WHERE teacher_id = ?", (teacher_id,))

    def get_assignments_for_student(self, group_id: int) -> List[Dict]:
        return []

    def get_students_management_keyboard_data(self, group_id: int) -> List[Dict]:
        students = self.get_group_students(group_id)
        return students if students else []