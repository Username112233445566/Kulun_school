import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_admin(telegram_id: int):
    conn = sqlite3.connect('kulun_school.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        user = cursor.fetchone()

        if user:
            cursor.execute(
                "UPDATE users SET role = 'admin', status = 'active' WHERE telegram_id = ?",
                (telegram_id,)
            )
            logger.info(f"User {telegram_id} set as admin")
        else:
            cursor.execute(
                "INSERT INTO users (telegram_id, full_name, phone, role, status) VALUES (?, ?, ?, ?, ?)",
                (telegram_id, "Администратор", "+79990000000", "admin", "active")
            )
            logger.info(f"New admin created with ID {telegram_id}")

        conn.commit()
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_admin(1952805890)