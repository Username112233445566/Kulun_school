import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional

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
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    role TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    group_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (group_id) REFERENCES groups (id)
                )
            ''')

            # Таблица групп
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS groups
                (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    teacher_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (teacher_id) REFERENCES users (id)
                )
            ''')

            # Таблица заданий
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS assignments
                (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    group_id INTEGER NOT NULL,
                    teacher_id INTEGER NOT NULL,
                    deadline TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (group_id) REFERENCES groups (id),
                    FOREIGN KEY (teacher_id) REFERENCES users (id)
                )
            ''')

            # Таблица посещаемости
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance
                (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    group_id INTEGER NOT NULL,
                    student_id INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    marked_by INTEGER NOT NULL,
                    marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (group_id) REFERENCES groups (id),
                    FOREIGN KEY (student_id) REFERENCES users (id),
                    FOREIGN KEY (marked_by) REFERENCES users (id)
                )
            ''')
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS grades
                           (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               student_id INTEGER NOT NULL,
                               group_id INTEGER NOT NULL,
                               subject TEXT NOT NULL,
                               grade INTEGER NOT NULL,
                               date DATE NOT NULL,
                               teacher_id INTEGER NOT NULL,
                               comment TEXT, 
                               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                               FOREIGN KEY(student_id) REFERENCES users(id),
                               FOREIGN KEY(group_id) REFERENCES groups(id),
                               FOREIGN KEY (teacher_id) REFERENCES users(id)
                               )
                           ''')

            # Таблица предметов (если нужно будет расширить)
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS subjects
                           (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               name TEXT UNIQUE
                               NOT NULL,
                               description TEXT,
                               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                           )
                           ''')
            # В методе init_db() добавим новую таблицу
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS schedule
                           (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               group_id INTEGER NOT NULL,
                               day_of_week TEXT NOT NULL,
                               start_time TEXT NOT NULL,
                               end_time TEXT NOT NULL,
                               subject TEXT NOT NULL, 
                               teacher_id INTEGER,
                               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                               FOREIGN KEY(group_id) REFERENCES groups(id),
                               FOREIGN KEY(teacher_id) REFERENCES users(id)
                               )
                           ''')

            conn.commit()
            logger.info("✅ База данных инициализирschedule_managerована")

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

    def user_exists(self, telegram_id: int) -> bool:
        """Проверить существование пользователя"""
        user = self.fetch_one(
            "SELECT id FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        return user is not None

    def group_exists(self, name: str) -> bool:
        """Проверить существование группы"""
        group = self.fetch_one(
            "SELECT id FROM groups WHERE name = ?",
            (name,)
        )
        return group is not None

    def get_user_groups(self, user_id: int) -> List[Dict]:
        """Получить группы пользователя"""
        return self.fetch_all(
            "SELECT g.* FROM groups g WHERE g.teacher_id = ? OR g.id IN (SELECT group_id FROM users WHERE id = ?)",
            (user_id, user_id)
        )