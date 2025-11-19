from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from services.user_manager import UserManager
from services.sync_manager import SyncManager

router = Router()

@router.message(Command("sync"))
async def cmd_sync(message: Message):
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        return await message.answer("Доступ запрещен")

    await message.answer("Начинаю синхронизацию с Google Sheets...")

    sync_manager = SyncManager()
    success = sync_manager.full_sync()

    if success:
        await message.answer("Синхронизация завершена!")
    else:
        await message.answer("Ошибка синхронизации. Проверьте логи.")

@router.message(Command("export"))
async def cmd_export(message: Message):
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        return await message.answer("Доступ запрещен")

    await message.answer("Экспортирую данные в Google Sheets...")

    sync_manager = SyncManager()
    sync_manager.sync_users_to_sheets()
    sync_manager.sync_groups_to_sheets()

    await message.answer("Экспорт завершен!")

@router.message(Command("import"))
async def cmd_import(message: Message):
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        return await message.answer("Доступ запрещен")

    await message.answer("Импортирую данные из Google Sheets...")

    sync_manager = SyncManager()
    success = sync_manager.sync_from_sheets()

    if success:
        await message.answer("Импорт завершен!")
    else:
        await message.answer("Ошибка импорта. Проверьте логи.")

@router.message(F.text == "Синхронизация")
async def sync_button(message: Message):
    await cmd_sync(message)

@router.callback_query(F.data == "cmd_sync")
async def cmd_sync_callback(callback: CallbackQuery):
    user_manager = UserManager()
    user = user_manager.get_user(callback.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        await callback.answer("Доступ запрещен")
        return

    await callback.message.answer("Начинаю синхронизацию с Google Sheets...")

    sync_manager = SyncManager()
    success = sync_manager.full_sync()

    if success:
        await callback.message.answer("Синхронизация завершена!")
    else:
        await callback.message.answer("Ошибка синхронизации. Проверьте логи.")

    await callback.answer()

@router.callback_query(F.data == "cmd_export")
async def cmd_export_callback(callback: CallbackQuery):
    user_manager = UserManager()
    user = user_manager.get_user(callback.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        await callback.answer("Доступ запрещен")
        return

    await callback.message.answer("Экспортирую данные в Google Sheets...")

    sync_manager = SyncManager()
    sync_manager.sync_users_to_sheets()
    sync_manager.sync_groups_to_sheets()

    await callback.message.answer("Экспорт завершен!")
    await callback.answer()

@router.callback_query(F.data == "cmd_import")
async def cmd_import_callback(callback: CallbackQuery):
    user_manager = UserManager()
    user = user_manager.get_user(callback.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        await callback.answer("Доступ запрещен")
        return

    await callback.message.answer("Импортирую данные из Google Sheets...")

    sync_manager = SyncManager()
    success = sync_manager.sync_from_sheets()

    if success:
        await callback.message.answer("Импорт завершен!")
    else:
        await callback.message.answer("Ошибка импорта. Проверьте логи.")

    await callback.answer()

@router.callback_query(F.data == "full_stats")
async def full_stats_callback(callback: CallbackQuery):
    user_manager = UserManager()
    user = user_manager.get_user(callback.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        await callback.answer("Доступ запрещен")
        return

    stats = user_manager.get_system_stats()

    reports_text = (
        "Полная статистика системы:\n\n"
        f"Всего пользователей: {stats['total_users']}\n"
        f"Активных: {stats['active_users']}\n"
        f"Ожидают подтверждения: {stats['pending_users']}\n\n"
        f"Учеников: {stats['students_count']}\n"
        f"Учителей: {stats['teachers_count']}\n"
        f"Групп: {stats['groups_count']}\n\n"
        f"Активность: высокая"
    )

    await callback.message.answer(reports_text)
    await callback.answer()