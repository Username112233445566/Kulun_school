from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards.admin import get_approval_keyboard, get_groups_selection_keyboard
from services.user_manager import UserManager

router = Router()

@router.message(F.text == "Пользователи")
async def admin_approval(message: Message):
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        return await message.answer("Доступ запрещен")

    pending_users = user_manager.get_pending_users()

    if not pending_users:
        await message.answer("Нет пользователей для подтверждения")
        return

    await message.answer(f"Найдено {len(pending_users)} пользователей для подтверждения:")

    for user_data in pending_users:
        role_display = "Ученик" if user_data['role'] == 'student' else "Учитель"

        user_info = (
            f"Новая заявка:\n\n"
            f"ФИО: {user_data['full_name']}\n"
            f"Телефон: {user_data['phone']}\n"
            f"Роль: {role_display}\n"
            f"Дата: {user_data['created_at']}"
        )

        await message.answer(
            user_info,
            reply_markup=get_approval_keyboard(user_data['telegram_id'])
        )

@router.callback_query(F.data.startswith("approve_"))
async def approve_user(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split("_")[1])
    user_manager = UserManager()

    user_data = user_manager.get_user(user_id)
    if not user_data:
        await callback.answer("Пользователь не найден")
        return

    role_display = "ученика" if user_data['role'] == 'student' else "учителя"

    await callback.message.edit_text(
        f"Выберите группу для {role_display} {user_data['full_name']}:",
        reply_markup=get_groups_selection_keyboard("assign_group", user_id)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("reject_"))
async def reject_user(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    user_manager = UserManager()

    user_data = user_manager.get_user(user_id)
    if user_data:
        user_manager.reject_user(user_id)
        await callback.message.edit_text(
            f"Заявка {user_data['full_name']} отклонена"
        )
    else:
        await callback.answer("Пользователь не найден")
    await callback.answer()

@router.callback_query(F.data.startswith("assign_group_"))
async def assign_group(callback: CallbackQuery):
    data_parts = callback.data.split("_")
    user_telegram_id = int(data_parts[2])
    group_id = int(data_parts[3])

    user_manager = UserManager()

    user_data = user_manager.get_user(user_telegram_id)
    group_data = user_manager.get_group(group_id)

    if not user_data:
        await callback.answer("Пользователь не найден")
        return

    if not group_data:
        await callback.answer("Группа не найден")
        return

    approval_success = user_manager.approve_user(user_telegram_id)
    if not approval_success:
        await callback.message.edit_text(
            f"Ошибка при подтверждении пользователя {user_data['full_name']}!"
        )
        await callback.answer()
        return

    if user_data['role'] == 'teacher':
        assignment_success = user_manager.assign_teacher_to_group(user_data['id'], group_id)
        role_action = "назначен учителем"
    else:
        assignment_success = user_manager.assign_user_to_group(user_data['id'], group_id)
        role_action = "добавлен в группу"

    if assignment_success:
        await callback.message.edit_text(
            f"Пользователь {user_data['full_name']} подтвержден и {role_action} '{group_data['name']}'!"
        )
    else:
        await callback.message.edit_text(
            f"Пользователь {user_data['full_name']} подтвержден, но произошла ошибка при назначении в группу!"
        )

    await callback.answer()