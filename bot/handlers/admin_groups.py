from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards.admin import (
    get_groups_selection_keyboard, get_group_management_keyboard,
    get_group_members_management_keyboard, get_students_management_keyboard,
    get_teachers_selection_keyboard, get_students_selection_keyboard,
    get_confirmation_keyboard
)
from services.user_manager import UserManager
from states.admin import AdminStates

router = Router()

# ========== ГРУППЫ ==========

@router.message(F.text == "🏫 Группы")
async def admin_groups(message: Message):
    """Просмотр всех групп"""
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        return await message.answer("❌ Доступ запрещен")

    groups = user_manager.get_all_groups()

    if not groups:
        await message.answer("📭 Нет созданных групп")
        return

    await message.answer(
        "🏫 Выберите группу для просмотра:",
        reply_markup=get_groups_selection_keyboard("group_info")
    )

@router.callback_query(F.data.startswith("group_info_"))
async def group_info(callback: CallbackQuery):
    """Просмотр информации о группе"""
    group_id = int(callback.data.split("_")[2])
    await show_group_info(callback.message, group_id)
    await callback.answer()

async def show_group_info(message: Message, group_id: int):
    """Показать информацию о группе"""
    user_manager = UserManager()

    group_details = user_manager.get_group_with_details(group_id)
    if not group_details:
        await message.answer("❌ Группа не найдена")
        return

    group_info_text = (
        f"🏫 Группа: {group_details['name']}\n"
        f"📅 Создана: {group_details['created_at']}\n\n"
    )

    # Информация о учителе
    if group_details.get('teacher'):
        group_info_text += f"👨‍🏫 Учитель: {group_details['teacher']['full_name']}\n"
    else:
        group_info_text += "👨‍🏫 Учитель: Не назначен\n"

    # Информация о учениках
    students_count = group_details['students_count']
    group_info_text += f"🎒 Учеников: {students_count}\n"

    if students_count > 0:
        group_info_text += "\n📋 Список учеников:\n"
        for i, student in enumerate(group_details['students'][:5], 1):
            group_info_text += f"{i}. {student['full_name']}\n"

        if students_count > 5:
            group_info_text += f"... и еще {students_count - 5} учеников\n"

    if isinstance(message, CallbackQuery):
        await message.message.edit_text(
            group_info_text,
            reply_markup=get_group_management_keyboard(group_id)
        )
    else:
        await message.answer(
            group_info_text,
            reply_markup=get_group_management_keyboard(group_id)
        )

@router.callback_query(F.data.startswith("group_members_"))
async def group_members(callback: CallbackQuery):
    """Просмотр участников группы"""
    group_id = int(callback.data.split("_")[2])
    user_manager = UserManager()

    group_details = user_manager.get_group_with_details(group_id)
    if not group_details:
        await callback.answer("❌ Группа не найдена")
        return

    members_text = f"👥 Участники группы {group_details['name']}:\n\n"

    # Учитель
    if group_details.get('teacher'):
        members_text += f"👨‍🏫 Учитель:\n{group_details['teacher']['full_name']}\n\n"
    else:
        members_text += "👨‍🏫 Учитель: Не назначен\n\n"

    # Ученики
    if group_details['students']:
        members_text += "🎒 Ученики:\n"
        for i, student in enumerate(group_details['students'], 1):
            members_text += f"{i}. {student['full_name']}\n"
            if student.get('phone'):
                members_text += f"   📞 {student['phone']}\n"
    else:
        members_text += "🎒 Учеников пока нет\n"

    await callback.message.edit_text(
        members_text,
        reply_markup=get_group_members_management_keyboard(group_id)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("manage_students_"))
async def manage_students(callback: CallbackQuery):
    """Управление учениками в группе"""
    group_id = int(callback.data.split("_")[2])
    user_manager = UserManager()

    group_details = user_manager.get_group_with_details(group_id)
    if not group_details:
        await callback.answer("❌ Группа не найдена")
        return

    if not group_details['students']:
        await callback.message.edit_text(
            f"В группе {group_details['name']} нет учеников для управления.",
            reply_markup=get_group_members_management_keyboard(group_id)
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        f"❌ Удаление учеников из группы {group_details['name']}:\n\n"
        "Нажмите на ученика, которого хотите удалить из группы:",
        reply_markup=get_students_management_keyboard(group_id, group_details['students'])
    )
    await callback.answer()

@router.callback_query(F.data.startswith("remove_student_"))
async def remove_student(callback: CallbackQuery):
    """Удаление ученика из группы"""
    data_parts = callback.data.split("_")
    group_id = int(data_parts[2])
    student_id = int(data_parts[3])

    user_manager = UserManager()

    # Получаем информацию об ученике
    student_data = user_manager.db.fetch_one(
        "SELECT * FROM users WHERE id = ?",
        (student_id,)
    )

    if not student_data:
        await callback.answer("❌ Ученик не найден")
        return

    # Удаляем ученика из группы
    if user_manager.remove_student_from_group(student_id):
        await callback.answer(f"✅ Ученик {student_data['full_name']} удален из группы!", show_alert=True)

        # Обновляем список учеников
        group_details = user_manager.get_group_with_details(group_id)
        if group_details and group_details['students']:
            await callback.message.edit_reply_markup(
                reply_markup=get_students_management_keyboard(group_id, group_details['students'])
            )
        else:
            await callback.message.edit_text(
                "✅ Все ученики удалены из группы!",
                reply_markup=get_group_members_management_keyboard(group_id)
            )
    else:
        await callback.answer("❌ Ошибка при удалении ученика из группы", show_alert=True)

@router.callback_query(F.data == "back_to_groups")
async def back_to_groups(callback: CallbackQuery):
    """Возврат к списку групп"""
    user_manager = UserManager()
    groups = user_manager.get_all_groups()

    if not groups:
        await callback.message.edit_text("📭 Нет созданных групп")
        return

    await callback.message.edit_text(
        "🏫 Выберите группу для просмотра:",
        reply_markup=get_groups_selection_keyboard("group_info")
    )
    await callback.answer()

# ========== РЕДАКТИРОВАНИЕ ГРУПП ==========

@router.callback_query(F.data.startswith("edit_group_name_"))
async def edit_group_name(callback: CallbackQuery, state: FSMContext):
    """Редактирование названия группы"""
    group_id = int(callback.data.split("_")[3])

    await state.set_state(AdminStates.editing_group_name)
    await state.update_data(group_id=group_id)

    await callback.message.edit_text("Введите новое название для группы:")
    await callback.answer()

@router.message(AdminStates.editing_group_name)
async def process_edit_group_name(message: Message, state: FSMContext):
    """Обработка нового названия группы"""
    new_name = message.text.strip()
    data = await state.get_data()
    group_id = data.get('group_id')

    if not new_name:
        await message.answer("❌ Название группы не может быть пустым. Введите название:")
        return

    user_manager = UserManager()

    if user_manager.update_group_name(group_id, new_name):
        await message.answer(f"✅ Название группы изменено на '{new_name}'!")
        await show_group_info(message, group_id)
    else:
        await message.answer("❌ Ошибка при изменении названия группы.")
        await show_group_info(message, group_id)

    await state.clear()

@router.callback_query(F.data.startswith("assign_teacher_"))
async def assign_teacher(callback: CallbackQuery, state: FSMContext):
    """Назначение учителя группе"""
    group_id = int(callback.data.split("_")[2])

    await state.update_data(current_group_id=group_id)

    user_manager = UserManager()
    group_data = user_manager.get_group(group_id)
    if not group_data:
        await callback.answer("❌ Группа не найдена")
        return

    await callback.message.edit_text(
        f"Выберите учителя для группы {group_data['name']}:",
        reply_markup=get_teachers_selection_keyboard(group_id)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("select_teacher_"))
async def select_teacher(callback: CallbackQuery):
    """Выбор учителя для группы"""
    data_parts = callback.data.split("_")
    group_id = int(data_parts[2])
    teacher_id = int(data_parts[3])

    user_manager = UserManager()
    group_data = user_manager.get_group(group_id)
    teacher_data = user_manager.get_user_by_id(teacher_id)

    if not group_data:
        await callback.answer("❌ Группа не найдена")
        return

    if not teacher_data:
        await callback.answer("❌ Учитель не найден")
        return

    if user_manager.assign_teacher_to_group(teacher_id, group_id):
        await callback.message.edit_text(
            f"✅ Учитель {teacher_data['full_name']} назначен на группу {group_data['name']}!"
        )
        await show_group_info(callback.message, group_id)
    else:
        await callback.message.edit_text(
            f"❌ Ошибка при назначении учителя {teacher_data['full_name']} на группу {group_data['name']}!"
        )
        await show_group_info(callback.message, group_id)

    await callback.answer()

@router.callback_query(F.data.startswith("remove_teacher_"))
async def remove_teacher(callback: CallbackQuery):
    """Удаление учителя из группы"""
    group_id = int(callback.data.split("_")[2])

    user_manager = UserManager()
    group_data = user_manager.get_group(group_id)

    if not group_data:
        await callback.answer("❌ Группа не найдена")
        return

    if user_manager.update_group_teacher(group_id, None):
        await callback.message.edit_text(
            f"✅ Учитель удален из группы {group_data['name']}!"
        )
        await show_group_info(callback.message, group_id)
    else:
        await callback.message.edit_text(
            f"❌ Ошибка при удалении учителя из группы {group_data['name']}!"
        )
        await show_group_info(callback.message, group_id)

    await callback.answer()

@router.callback_query(F.data.startswith("add_students_"))
async def add_students(callback: CallbackQuery, state: FSMContext):
    """Добавление учеников в группу"""
    group_id = int(callback.data.split("_")[2])

    await state.update_data(current_group_id=group_id)

    user_manager = UserManager()
    group_data = user_manager.get_group(group_id)
    if not group_data:
        await callback.answer("❌ Группа не найдена")
        return

    students = user_manager.get_students_without_groups()

    if not students:
        await callback.message.edit_text(
            f"📭 Нет учеников без групп для добавления в {group_data['name']}.\n\n"
            "Все ученики уже распределены по группам.",
            reply_markup=get_group_members_management_keyboard(group_id)
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        f"Выберите учеников для добавления в группу {group_data['name']}:",
        reply_markup=get_students_selection_keyboard(group_id)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("select_student_"))
async def select_student(callback: CallbackQuery):
    """Выбор ученика для добавления в группу"""
    data_parts = callback.data.split("_")
    group_id = int(data_parts[2])
    student_id = int(data_parts[3])

    user_manager = UserManager()
    group_data = user_manager.get_group(group_id)
    student_data = user_manager.get_user_by_id(student_id)

    if not group_data:
        await callback.answer("❌ Группа не найдена", show_alert=True)
        return

    if not student_data:
        await callback.answer("❌ Ученик не найден", show_alert=True)
        return

    if user_manager.assign_user_to_group(student_id, group_id):
        await callback.answer(
            f"✅ Ученик {student_data['full_name']} добавлен в группу {group_data['name']}!",
            show_alert=False
        )

        students = user_manager.get_students_without_groups()

        if students:
            await callback.message.edit_reply_markup(
                reply_markup=get_students_selection_keyboard(group_id)
            )
        else:
            await callback.message.edit_text(
                "✅ Все доступные ученики добавлены в группу!",
                reply_markup=get_group_members_management_keyboard(group_id)
            )
    else:
        await callback.answer(
            f"❌ Ошибка при добавлении ученика {student_data['full_name']} в группу {group_data['name']}!",
            show_alert=True
        )

@router.callback_query(F.data.startswith("delete_group_"))
async def delete_group_confirmation(callback: CallbackQuery):
    """Подтверждение удаления группы"""
    group_id = int(callback.data.split("_")[2])
    user_manager = UserManager()

    group_data = user_manager.get_group(group_id)
    if not group_data:
        await callback.answer("❌ Группа не найдена")
        return

    students = user_manager.get_group_students(group_id)

    warning_text = ""
    if students:
        warning_text = f"\n\n⚠️ В группе есть {len(students)} учеников! Они будут перемещены без группы."

    await callback.message.edit_text(
        f"Вы уверены, что хотите удалить группу '{group_data['name']}'?{warning_text}",
        reply_markup=get_confirmation_keyboard("delete_group", group_id)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("confirm_delete_group_"))
async def confirm_delete_group(callback: CallbackQuery):
    """Подтвержденное удаление группы"""
    group_id = int(callback.data.split("_")[3])
    user_manager = UserManager()

    group_data = user_manager.get_group(group_id)
    if not group_data:
        await callback.answer("❌ Группа не найдена")
        return

    if user_manager.delete_group(group_id):
        await callback.message.edit_text(f"✅ Группа '{group_data['name']}' успешно удалена!")

        groups = user_manager.get_all_groups()
        if groups:
            await callback.message.answer(
                "🏫 Выберите группу для просмотра:",
                reply_markup=get_groups_selection_keyboard("group_info")
            )
        else:
            await callback.message.answer("📭 Нет созданных групп")
    else:
        await callback.message.edit_text("❌ Ошибка при удалении группы.")

    await callback.answer()

@router.callback_query(F.data.startswith("cancel_delete_group_"))
async def cancel_delete_group(callback: CallbackQuery):
    """Отмена удаления группы"""
    group_id = int(callback.data.split("_")[3])
    await group_info(callback)
    await callback.answer()

@router.callback_query(F.data.startswith("group_stats_"))
async def group_stats(callback: CallbackQuery):
    """Статистика группы"""
    group_id = int(callback.data.split("_")[2])
    user_manager = UserManager()

    group_details = user_manager.get_group_with_details(group_id)
    if not group_details:
        await callback.answer("❌ Группа не найдена")
        return

    stats_text = (
        f"📊 Статистика группы: {group_details['name']}\n\n"
        f"👨‍🏫 Учитель: {group_details['teacher']['full_name'] if group_details.get('teacher') else 'Не назначен'}\n"
        f"🎒 Учеников: {group_details['students_count']}\n"
        f"📅 Создана: {group_details['created_at']}\n\n"
    )

    if group_details['students']:
        stats_text += "📋 Список учеников:\n"
        for i, student in enumerate(group_details['students'], 1):
            stats_text += f"{i}. {student['full_name']}\n"

    await callback.message.edit_text(
        stats_text,
        reply_markup=get_group_management_keyboard(group_id)
    )
    await callback.answer()