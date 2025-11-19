import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_admin(telegram_id: int):
    """Принудительно назначает пользователя администратором"""
    conn = sqlite3.connect('kulun_school.db')
    cursor = conn.cursor()

    try:
        # Проверяем существование пользователя
        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        user = cursor.fetchone()

        if user:
            # Обновляем роль и статус
            cursor.execute(
                "UPDATE users SET role = 'admin', status = 'active' WHERE telegram_id = ?",
                (telegram_id,)
            )
            logger.info(f"✅ Пользователь {telegram_id} назначен администратором")
        else:
            # Создаем нового администратора
            cursor.execute(
                "INSERT INTO users (telegram_id, full_name, phone, role, status) VALUES (?, ?, ?, ?, ?)",
                (telegram_id, "Администратор", "+79990000000", "admin", "active")
            )
            logger.info(f"✅ Создан новый администратор с ID {telegram_id}")

        conn.commit()

    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    # Замените на ваш реальный Telegram ID
    fix_admin(1952805890)