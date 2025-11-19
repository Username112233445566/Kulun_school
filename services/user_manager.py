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
        """Создает администратора по умолчанию если его нет"""
        admin_id = 1952805890  # Ваш реальный ID

        admin = self.get_user(admin_id)
        if not admin:
            logger.info("Создаем администратора по умолчанию...")
            success = self.create_user(
                telegram_id=admin_id,
                full_name="Администратор",
                phone="+79990000000",
                role="admin"
            )
            if success:
                # Активируем администратора
                self.db.execute(
                    "UPDATE users SET status = 'active' WHERE telegram_id = ?",
                    (admin_id,)
                )
                logger.info("✅ Администратор создан")
            else:
                logger.error("❌ Ошибка при создании администратора")
        else:
            # Проверяем, что существующий администратор активен
            if admin['status'] != 'active':
                self.db.execute(
                    "UPDATE users SET status = 'active' WHERE telegram_id = ?",
                    (admin_id,)
                )
                logger.info("✅ Администратор активирован")

    def create_user(self, telegram_id: int, full_name: str, phone: str, role: str) -> bool:
        """Создать нового пользователя БЕЗ автоматической синхронизации"""
        try:
            self.db.execute(
                "INSERT INTO users (telegram_id, full_name, phone, role) VALUES (?, ?, ?, ?)",
                (telegram_id, full_name, phone, role)
            )
            logger.info(f"✅ Пользователь {full_name} создан")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"⚠️ Пользователь {telegram_id} уже существует")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка при создании пользователя: {e}")
            return False

    def get_user(self, telegram_id: int) -> Optional[Dict]:
        """Получить пользователя по Telegram ID"""
        return self.db.fetch_one(
            "SELECT * FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Получить пользователя по внутреннему ID (а не telegram_id)"""
        return self.db.fetch_one(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )

    def approve_user(self, telegram_id: int) -> bool:
        """Подтвердить пользователя БЕЗ автоматической синхронизации"""
        try:
            self.db.execute(
                "UPDATE users SET status = 'active' WHERE telegram_id = ?",
                (telegram_id,)
            )
            logger.info(f"✅ Пользователь {telegram_id} подтвержден")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при подтверждении пользователя: {e}")
            return False

    def assign_user_to_group(self, user_id: int, group_id: int) -> bool:
        """Назначить пользователя в группу БЕЗ автоматической синхронизации"""
        try:
            # Получаем пользователя по ID
            user = self.get_user_by_id(user_id)
            if not user:
                logger.error(f"❌ Пользователь с ID {user_id} не найден")
                return False

            # Обновляем группу пользователя
            self.db.execute(
                "UPDATE users SET group_id = ? WHERE id = ?",
                (group_id, user_id)
            )
            logger.info(f"✅ Пользователь {user['full_name']} (ID: {user_id}) назначен в группу {group_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при назначении пользователя в группу: {e}")
            return False

    def assign_teacher_to_group(self, teacher_id: int, group_id: int) -> bool:
        """Назначить учителя на группу БЕЗ автоматической синхронизации"""
        try:
            # Получаем учителя по ID
            teacher = self.get_user_by_id(teacher_id)
            if not teacher:
                logger.error(f"❌ Учитель с ID {teacher_id} не найден")
                return False

            # Проверяем группу
            group = self.get_group(group_id)
            if not group:
                logger.error(f"❌ Группа с ID {group_id} не найдена")
                return False

            # Обновляем учителя группы
            self.db.execute(
                "UPDATE groups SET teacher_id = ? WHERE id = ?",
                (teacher_id, group_id)
            )
            logger.info(f"✅ Учитель {teacher['full_name']} (ID: {teacher_id}) назначен на группу {group['name']}")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при назначении учителя на группу: {e}")
            return False

    def update_group_teacher(self, group_id: int, teacher_id: int = None) -> bool:
        """Обновить учителя группы БЕЗ автоматической синхронизации"""
        try:
            # Проверяем группу
            group = self.get_group(group_id)
            if not group:
                logger.error(f"❌ Группа с ID {group_id} не найдена")
                return False

            # Если teacher_id указан, проверяем учителя
            if teacher_id:
                teacher = self.get_user_by_id(teacher_id)
                if not teacher:
                    logger.error(f"❌ Учитель с ID {teacher_id} не найден")
                    return False

            # Обновляем учителя группы
            self.db.execute(
                "UPDATE groups SET teacher_id = ? WHERE id = ?",
                (teacher_id, group_id)
            )

            action = "назначен" if teacher_id else "удален"
            logger.info(f"✅ Учитель {action} для группы {group['name']}")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при обновлении учителя группы: {e}")
            return False

    def reject_user(self, telegram_id: int) -> bool:
        """Отклонить пользователя БЕЗ автоматической синхронизации"""
        try:
            self.db.execute(
                "UPDATE users SET status = 'rejected' WHERE telegram_id = ?",
                (telegram_id,)
            )
            logger.info(f"❌ Пользователь {telegram_id} отклонен")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при отклонении пользователя: {e}")
            return False

    def get_pending_users(self) -> List[Dict]:
        """Получить список пользователей ожидающих подтверждения"""
        return self.db.fetch_all(
            "SELECT * FROM users WHERE status = 'pending'"
        )

    def create_group(self, name: str, teacher_id: int = None) -> bool:
        """Создать новую группу БЕЗ автоматической синхронизации"""
        try:
            self.db.execute(
                "INSERT INTO groups (name, teacher_id) VALUES (?, ?)",
                (name, teacher_id)
            )
            logger.info(f"✅ Группа {name} создана")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при создании группы: {e}")
            return False

    def get_all_groups(self) -> List[Dict]:
        """Получить все группы"""
        return self.db.fetch_all("SELECT * FROM groups")

    def get_group(self, group_id: int) -> Optional[Dict]:
        """Получить группу по ID"""
        return self.db.fetch_one("SELECT * FROM groups WHERE id = ?", (group_id,))

    def get_group_with_details(self, group_id: int) -> Optional[Dict]:
        """Получить группу с детальной информацией"""
        group = self.get_group(group_id)
        if not group:
            return None

        # Получаем учителя
        teacher = None
        if group.get('teacher_id'):
            teacher = self.get_user_by_id(group['teacher_id'])

        # Получаем учеников
        students = self.get_group_students(group_id)

        return {
            **group,
            'teacher': teacher,
            'students': students,
            'students_count': len(students)
        }

    def get_group_students(self, group_id: int) -> List[Dict]:
        """Получить учеников группы"""
        return self.db.fetch_all(
            "SELECT * FROM users WHERE group_id = ? AND role = 'student' AND status = 'active'",
            (group_id,)
        )

    def get_students_without_groups(self) -> List[Dict]:
        """Получить учеников без групп"""
        return self.db.fetch_all(
            "SELECT * FROM users WHERE role = 'student' AND status = 'active' AND (group_id IS NULL OR group_id = '')"
        )

    def get_available_teachers(self) -> List[Dict]:
        """Получить всех доступных учителей (активных)"""
        return self.db.fetch_all(
            "SELECT * FROM users WHERE role = 'teacher' AND status = 'active'"
        )

    def get_active_students(self) -> List[Dict]:
        """Получить всех активных учеников"""
        return self.db.fetch_all(
            "SELECT * FROM users WHERE role = 'student' AND status = 'active'"
        )

    def remove_student_from_group(self, student_id: int) -> bool:
        """Удалить ученика из группы БЕЗ автоматической синхронизации"""
        try:
            self.db.execute(
                "UPDATE users SET group_id = NULL WHERE id = ?",
                (student_id,)
            )
            logger.info(f"✅ Ученик {student_id} удален из группы")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при удалении ученика из группы: {e}")
            return False

    def delete_group(self, group_id: int) -> bool:
        """Удалить группу БЕЗ автоматической синхронизации"""
        try:
            # Сначала обнуляем group_id у всех пользователей этой группы
            self.db.execute(
                "UPDATE users SET group_id = NULL WHERE group_id = ?",
                (group_id,)
            )

            # Затем удаляем саму группу
            self.db.execute(
                "DELETE FROM groups WHERE id = ?",
                (group_id,)
            )

            logger.info(f"✅ Группа {group_id} удалена")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при удалении группы: {e}")
            return False

    def update_group_name(self, group_id: int, new_name: str) -> bool:
        """Обновить название группы БЕЗ автоматической синхронизации"""
        try:
            self.db.execute(
                "UPDATE groups SET name = ? WHERE id = ?",
                (new_name, group_id)
            )
            logger.info(f"✅ Название группы {group_id} изменено на {new_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при изменении названия группы: {e}")
            return False

    def get_system_stats(self) -> Dict:
        """Получить статистику системы"""
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
        """Получить группы учителя"""
        return self.db.fetch_all(
            "SELECT * FROM groups WHERE teacher_id = ?",
            (teacher_id,)
        )

    def get_assignments_for_student(self, group_id: int) -> List[Dict]:
        """Получить задания для ученика группы (заглушка)"""
        # TODO: Реализовать получение заданий из Google Sheets или базы данных
        return []

    def get_students_management_keyboard_data(self, group_id: int) -> List[Dict]:
        """Получить данные для клавиатуры управления учениками"""
        students = self.get_group_students(group_id)
        return students if students else []