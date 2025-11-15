import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional
from services.google_sheets import GoogleSheetsManager

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path="kulun_school.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Инициализация базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Таблица пользователей
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS users
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               telegram_id
                               INTEGER
                               UNIQUE
                               NOT
                               NULL,
                               full_name
                               TEXT
                               NOT
                               NULL,
                               phone
                               TEXT
                               NOT
                               NULL,
                               role
                               TEXT
                               NOT
                               NULL,
                               status
                               TEXT
                               DEFAULT
                               'pending',
                               group_id
                               INTEGER,
                               created_at
                               TIMESTAMP
                               DEFAULT
                               CURRENT_TIMESTAMP,
                               FOREIGN
                               KEY
                           (
                               group_id
                           ) REFERENCES groups
                           (
                               id
                           )
                               )
                           ''')

            # Таблица групп
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS groups
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               name
                               TEXT
                               UNIQUE
                               NOT
                               NULL,
                               teacher_id
                               INTEGER,
                               created_at
                               TIMESTAMP
                               DEFAULT
                               CURRENT_TIMESTAMP,
                               FOREIGN
                               KEY
                           (
                               teacher_id
                           ) REFERENCES users
                           (
                               id
                           )
                               )
                           ''')

            conn.commit()
            logger.info("✅ База данных инициализирована")

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Выполнить SQL запрос"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Получить одну запись"""
        cursor = self.execute(query, params)
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        if row:
            return dict(zip(columns, row))
        return None

    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
        """Получить все записи"""
        cursor = self.execute(query, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


class SyncManager:
    def __init__(self):
        self.db = Database()
        self.sheets = GoogleSheetsManager()

    def sync_users_to_sheets(self):
        """Синхронизирует пользователей из SQLite в Google Sheets"""
        try:
            users = self.db.fetch_all("SELECT * FROM users")
            worksheet = self.sheets.get_worksheet("Users")

            if not worksheet:
                logger.error("❌ Не удалось получить лист Users")
                return False

            # Очищаем и обновляем заголовки
            worksheet.clear()
            worksheet.append_row([
                "ID", "Telegram ID", "Full Name", "Phone", "Role",
                "Status", "Group ID", "Group Name", "Created At"
            ])

            for user in users:
                group_name = ""
                if user.get('group_id'):
                    group = self.db.fetch_one(
                        "SELECT name FROM groups WHERE id = ?",
                        (user['group_id'],)
                    )
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

            logger.info("✅ Пользователи синхронизированы в Google Sheets")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка синхронизации пользователей: {e}")
            return False

    def sync_groups_to_sheets(self):
        """Синхронизирует группы из SQLite в Google Sheets"""
        try:
            groups = self.db.fetch_all("""
                                       SELECT g.*, u.full_name as teacher_name
                                       FROM groups g
                                                LEFT JOIN users u ON g.teacher_id = u.id
                                       """)
            worksheet = self.sheets.get_worksheet("Groups")

            if not worksheet:
                logger.error("❌ Не удалось получить лист Groups")
                return False

            worksheet.clear()
            worksheet.append_row([
                "ID", "Name", "Teacher ID", "Teacher Name",
                "Students Count", "Created At"
            ])

            for group in groups:
                # Считаем количество учеников в группе
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

            logger.info("✅ Группы синхронизированы в Google Sheets")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка синхронизации групп: {e}")
            return False


class UserManager:
    def __init__(self):
        self.db = Database()
        self.sync_manager = SyncManager()
        self._ensure_admin_exists()

    def _ensure_admin_exists(self):
        """Создает администратора по умолчанию если его нет"""
        # ЗАМЕНИ ЭТОТ ID НА СВОЙ TELEGRAM ID
        admin_id = 2128869013  # Замени на свой реальный ID

        admin = self.get_user(admin_id)
        if not admin:
            logger.info("Создаем администратора по умолчанию...")
            self.create_user(
                telegram_id=admin_id,
                full_name="Администратор",
                phone="+79990000000",
                role="admin"
            )
            # Активируем администратора
            self.db.execute(
                "UPDATE users SET status = 'active' WHERE telegram_id = ?",
                (admin_id,)
            )
            logger.info("✅ Администратор создан")

            # Синхронизируем с Google Sheets
            self.sync_manager.sync_users_to_sheets()

    def create_user(self, telegram_id: int, full_name: str, phone: str, role: str) -> bool:
        """Создать нового пользователя с синхронизацией"""
        try:
            self.db.execute(
                "INSERT INTO users (telegram_id, full_name, phone, role) VALUES (?, ?, ?, ?)",
                (telegram_id, full_name, phone, role)
            )
            logger.info(f"✅ Пользователь {full_name} создан")

            # Синхронизируем с Google Sheets
            self.sync_manager.sync_users_to_sheets()
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
        """Подтвердить пользователя"""
        try:
            self.db.execute(
                "UPDATE users SET status = 'active' WHERE telegram_id = ?",
                (telegram_id,)
            )
            logger.info(f"✅ Пользователь {telegram_id} подтвержден")

            # Синхронизируем с Google Sheets
            self.sync_manager.sync_users_to_sheets()
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при подтверждении пользователя: {e}")
            return False

    def assign_user_to_group(self, user_id: int, group_id: int) -> bool:
        """Назначить пользователя в группу (исправленная версия)"""
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

            # Синхронизируем с Google Sheets
            self.sync_manager.sync_users_to_sheets()
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при назначении пользователя в группу: {e}")
            return False

    def assign_teacher_to_group(self, teacher_id: int, group_id: int) -> bool:
        """Назначить учителя на группу (исправленная версия)"""
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

            # Синхронизируем с Google Sheets
            self.sync_manager.sync_groups_to_sheets()
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при назначении учителя на группу: {e}")
            return False

    def update_group_teacher(self, group_id: int, teacher_id: int = None) -> bool:
        """Обновить учителя группы (исправленная версия)"""
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

            # Синхронизируем с Google Sheets
            self.sync_manager.sync_groups_to_sheets()
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при обновлении учителя группы: {e}")
            return False

    def reject_user(self, telegram_id: int) -> bool:
        """Отклонить пользователя"""
        try:
            self.db.execute(
                "UPDATE users SET status = 'rejected' WHERE telegram_id = ?",
                (telegram_id,)
            )
            logger.info(f"❌ Пользователь {telegram_id} отклонен")

            # Синхронизируем с Google Sheets
            self.sync_manager.sync_users_to_sheets()
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
        """Создать новую группу с синхронизацией"""
        try:
            self.db.execute(
                "INSERT INTO groups (name, teacher_id) VALUES (?, ?)",
                (name, teacher_id)
            )
            logger.info(f"✅ Группа {name} создана")

            # Синхронизируем с Google Sheets
            self.sync_manager.sync_groups_to_sheets()
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при создании группы: {e}")
            return False

    def get_all_groups(self) -> List[Dict]:
        """Получить все группы"""
        return self.db.fetch_all(
            "SELECT * FROM groups"
        )

    def get_group(self, group_id: int) -> Optional[Dict]:
        """Получить группу по ID"""
        return self.db.fetch_one(
            "SELECT * FROM groups WHERE id = ?",
            (group_id,)
        )

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
        """Получить учеников без групп (исправленная версия)"""
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
        """Удалить ученика из группы"""
        try:
            self.db.execute(
                "UPDATE users SET group_id = NULL WHERE id = ?",
                (student_id,)
            )
            logger.info(f"✅ Ученик {student_id} удален из группы")

            # Синхронизируем с Google Sheets
            self.sync_manager.sync_users_to_sheets()
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при удалении ученика из группы: {e}")
            return False

    def delete_group(self, group_id: int) -> bool:
        """Удалить группу"""
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

            # Синхронизируем с Google Sheets
            self.sync_manager.sync_groups_to_sheets()
            self.sync_manager.sync_users_to_sheets()
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при удалении группы: {e}")
            return False

    def update_group_name(self, group_id: int, new_name: str) -> bool:
        """Обновить название группы"""
        try:
            self.db.execute(
                "UPDATE groups SET name = ? WHERE id = ?",
                (new_name, group_id)
            )
            logger.info(f"✅ Название группы {group_id} изменено на {new_name}")

            # Синхронизируем с Google Sheets
            self.sync_manager.sync_groups_to_sheets()
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при изменении названия группы: {e}")
            return False

    def get_system_stats(self) -> Dict:
        """Получить статистику системы"""
        total_users = self.db.fetch_one("SELECT COUNT(*) as count FROM users")['count']
        active_users = self.db.fetch_one("SELECT COUNT(*) as count FROM users WHERE status = 'active'")['count']
        pending_users = self.db.fetch_one("SELECT COUNT(*) as count FROM users WHERE status = 'pending'")['count']
        students_count = \
        self.db.fetch_one("SELECT COUNT(*) as count FROM users WHERE role = 'student' AND status = 'active'")['count']
        teachers_count = \
        self.db.fetch_one("SELECT COUNT(*) as count FROM users WHERE role = 'teacher' AND status = 'active'")['count']
        groups_count = self.db.fetch_one("SELECT COUNT(*) as count FROM groups")['count']

        return {
            'total_users': total_users,
            'active_users': active_users,
            'pending_users': pending_users,
            'students_count': students_count,
            'teachers_count': teachers_count,
            'groups_count': groups_count
        }