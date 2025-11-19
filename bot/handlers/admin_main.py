from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.keyboards.admin import get_admin_keyboard, get_reports_keyboard
from services.user_manager import UserManager
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Панель администратора"""
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    logger.info(f"Проверка прав администратора для пользователя {message.from_user.id}: {user}")

    if not user:
        await message.answer("❌ Пользователь не найден в системе")
        return

    if user['role'] != 'admin':
        await message.answer(f"❌ Ваша роль: {user['role']}. Требуется роль 'admin'")
        return

    if user['status'] != 'active':
        await message.answer(f"❌ Ваш статус: {user['status']}. Требуется статус 'active'")
        return

    await message.answer(
        "⚙️ Панель администратора",
        reply_markup=get_admin_keyboard()
    )

@router.message(F.text == "📊 Отчеты")
async def admin_reports(message: Message):
    """Просмотр отчетов системы"""
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    logger.info(f"Обработка отчетов для пользователя {message.from_user.id}: {user}")

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        return await message.answer("❌ Доступ запрещен")

    stats = user_manager.get_system_stats()

    reports_text = (
        "📊 Отчеты системы:\n\n"
        f"👥 Всего пользователей: {stats['total_users']}\n"
        f"✅ Активных: {stats['active_users']}\n"
        f"⏳ Ожидают: {stats['pending_users']}\n\n"
        f"🎒 Учеников: {stats['students_count']}\n"
        f"👨‍🏫 Учителей: {stats['teachers_count']}\n"
        f"🏫 Групп: {stats['groups_count']}"
    )

    await message.answer(reports_text, reply_markup=get_reports_keyboard())

# Перенесите эти команды на верхний уровень (убрав вложенность)
@router.message(Command("status"))
async def check_status(message: Message):
    """Проверка статуса пользователя"""
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if user:
        status_info = (
            f"👤 Ваш статус:\n"
            f"ID: {user['id']}\n"
            f"Telegram ID: {user['telegram_id']}\n"
            f"ФИО: {user['full_name']}\n"
            f"Роль: {user['role']}\n"
            f"Статус: {user['status']}\n"
            f"Группа: {user.get('group_id', 'Не назначена')}"
        )
    else:
        status_info = "❌ Вы не зарегистрированы в системе"

    await message.answer(status_info)

@router.message(Command("users"))
async def list_users(message: Message):
    """Показать всех пользователей (для отладки)"""
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        return await message.answer("❌ Доступ запрещен")

    all_users = user_manager.db.fetch_all("SELECT * FROM users")

    users_text = "👥 Все пользователи:\n\n"
    for u in all_users:
        users_text += f"ID: {u['id']}, TG: {u['telegram_id']}, Имя: {u['full_name']}, Роль: {u['role']}, Статус: {u['status']}\n"

    await message.answer(users_text[:4000])


@router.message(Command("subjects"))
async def manage_subjects_command(message: Message):
    """Управление предметами через команду /subjects"""
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        return await message.answer("❌ Доступ запрещен")

    from bot.keyboards.admin import get_subjects_management_keyboard

    subjects_manager = SubjectsManager()
    subjects = subjects_manager.get_all_subjects()

    if not subjects:
        await message.answer("📚 Нет добавленных предметов")
        return

    subjects_text = "📚 Список предметов:\n\n"
    for subject in subjects:
        subjects_text += f"🆔 {subject['id']}. {subject['name']}"
        if subject.get('description'):
            subjects_text += f" - {subject['description']}"
        subjects_text += "\n"

    await message.answer(
        subjects_text,
        reply_markup=get_subjects_management_keyboard()
    )