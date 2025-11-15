from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.keyboards.admin import (
    get_admin_keyboard, get_approval_keyboard, get_groups_selection_keyboard,
    get_group_management_keyboard, get_group_members_management_keyboard,
    get_students_management_keyboard, get_teachers_selection_keyboard,
    get_students_selection_keyboard, get_confirmation_keyboard, get_reports_keyboard
)
from services.user_manager import UserManager, SyncManager
from states.admin import AdminStates

router = Router()


# ========== КОМАНДЫ ==========

@router.message(Command("sync"))
async def cmd_sync(message: Message):
    """Команда синхронизации с Google Sheets"""
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        return await message.answer("❌ Доступ запрещен")

    await message.answer("🔄 Начинаю синхронизацию с Google Sheets...")

    sync_manager = SyncManager()
    success = sync_manager.full_sync()

    if success:
        await message.answer("✅ Синхронизация завершена!")
    else:
        await message.answer("❌ Ошибка синхронизации. Проверьте логи.")


@router.message(Command("export"))
async def cmd_export(message: Message):
    """Экспорт данных в Google Sheets"""
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        return await message.answer("❌ Доступ запрещен")

    await message.answer("📤 Экспортирую данные в Google Sheets...")

    sync_manager = SyncManager()
    sync_manager.sync_users_to_sheets()
    sync_manager.sync_groups_to_sheets()

    await message.answer("✅ Экспорт завершен!")


@router.message(Command("import"))
async def cmd_import(message: Message):
    """Импорт данных из Google Sheets"""
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        return await message.answer("❌ Доступ запрещен")

    await message.answer("📥 Импортирую данные из Google Sheets...")

    sync_manager = SyncManager()
    success = sync_manager.sync_from_sheets()

    if success:
        await message.answer("✅ Импорт завершен!")
    else:
        await message.answer("❌ Ошибка импорта. Проверьте логи.")


@router.message(Command("creategroup"))
async def cmd_create_group(message: Message, state: FSMContext):
    """Команда создания группы"""
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        return await message.answer("❌ Доступ запрещен")

    await state.set_state(AdminStates.creating_group)
    await message.answer("Введите название для новой группы:")


# ========== ОСНОВНОЙ ФУНКЦИОНАЛ ==========

@router.message(F.text == "👤 Подтверждение")
async def admin_approval(message: Message):
    """Просмотр пользователей для подтверждения"""
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        return await message.answer("❌ Доступ запрещен")

    pending_users = user_manager.get_pending_users()

    if not pending_users:
        await message.answer("📭 Нет пользователей для подтверждения")
        return

    await message.answer(f"📋 Найдено {len(pending_users)} пользователей для подтверждения:")

    for user_data in pending_users:
        role_display = "🎒 Ученик" if user_data['role'] == 'student' else "👨‍🏫 Учитель"

        user_info = (
            f"🆕 Новая заявка:\n\n"
            f"👤 ФИО: {user_data['full_name']}\n"
            f"📞 Телефон: {user_data['phone']}\n"
            f"🎯 Роль: {role_display}\n"
            f"📅 Дата: {user_data['created_at']}"
        )

        await message.answer(
            user_info,
            reply_markup=get_approval_keyboard(user_data['telegram_id'])
        )


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


@router.message(F.text == "📊 Отчеты")
async def admin_reports(message: Message):
    """Просмотр отчетов системы"""
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

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


@router.message(F.text == "🔄 Синхронизация")
async def sync_button(message: Message):
    """Обработка кнопки синхронизации"""
    await cmd_sync(message)


@router.message(F.text == "📤 Экспорт")
async def export_button(message: Message):
    """Обработка кнопки экспорта"""
    await cmd_export(message)


@router.message(F.text == "📥 Импорт")
async def import_button(message: Message):
    """Обработка кнопки импорта"""
    await cmd_import(message)


@router.message(F.text == "➕ Создать группу")
async def create_group_button(message: Message, state: FSMContext):
    """Обработка кнопки создания группы"""
    await cmd_create_group(message, state)


# ========== ОБРАБОТЧИКИ CALLBACK ==========

@router.callback_query(F.data.startswith("approve_"))
async def approve_user(callback: CallbackQuery, state: FSMContext):
    """Подтверждение пользователя"""
    user_id = int(callback.data.split("_")[1])
    user_manager = UserManager()

    user_data = user_manager.get_user(user_id)
    if not user_data:
        await callback.answer("❌ Пользователь не найден")
        return

    # Для ВСЕХ пользователей предлагаем выбрать группу
    role_display = "ученика" if user_data['role'] == 'student' else "учителя"

    await callback.message.edit_text(
        f"Выберите группу для {role_display} {user_data['full_name']}:",
        reply_markup=get_groups_selection_keyboard("assign_group", user_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("reject_"))
async def reject_user(callback: CallbackQuery):
    """Отклонение пользователя"""
    user_id = int(callback.data.split("_")[1])
    user_manager = UserManager()

    user_data = user_manager.get_user(user_id)
    if user_data:
        user_manager.reject_user(user_id)
        await callback.message.edit_text(
            f"❌ Заявка {user_data['full_name']} отклонена"
        )
    else:
        await callback.answer("❌ Пользователь не найден")

    await callback.answer()


@router.callback_query(F.data.startswith("assign_group_"))
async def assign_group(callback: CallbackQuery):
    """Назначение пользователя в группу (ИСПРАВЛЕННАЯ ВЕРСИЯ)"""
    data_parts = callback.data.split("_")
    user_telegram_id = int(data_parts[2])  # Это telegram_id пользователя
    group_id = int(data_parts[3])

    user_manager = UserManager()

    # Получаем пользователя по telegram_id
    user_data = user_manager.get_user(user_telegram_id)
    group_data = user_manager.get_group(group_id)

    if not user_data:
        await callback.answer("❌ Пользователь не найден")
        return

    if not group_data:
        await callback.answer("❌ Группа не найдена")
        return

    # Подтверждаем пользователя
    approval_success = user_manager.approve_user(user_telegram_id)
    if not approval_success:
        await callback.message.edit_text(
            f"❌ Ошибка при подтверждении пользователя {user_data['full_name']}!"
        )
        await callback.answer()
        return


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


# ========== ФУНКЦИОНАЛ РЕДАКТИРОВАНИЯ ГРУПП ==========

@router.callback_query(F.data.startswith("edit_group_name_"))
async def edit_group_name(callback: CallbackQuery, state: FSMContext):
    """Редактирование названия группы"""
    group_id = int(callback.data.split("_")[3])

    await state.set_state(AdminStates.editing_group_name)
    await state.update_data(group_id=group_id)

    await callback.message.edit_text(
        "Введите новое название для группы:"
    )
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
        # Возвращаемся к информации о группе
        await show_group_info(message, group_id)
    else:
        await message.answer("❌ Ошибка при изменении названия группы.")
        # Все равно возвращаемся к информации о группе
        await show_group_info(message, group_id)

    await state.clear()


@router.callback_query(F.data.startswith("assign_teacher_"))
async def assign_teacher(callback: CallbackQuery, state: FSMContext):
    """Назначение учителя группе"""
    group_id = int(callback.data.split("_")[2])

    # Сохраняем group_id в состоянии для возврата
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
    """Выбор учителя для группы (ИСПРАВЛЕННАЯ ВЕРСИЯ)"""
    data_parts = callback.data.split("_")
    group_id = int(data_parts[2])
    teacher_id = int(data_parts[3])  # Это внутренний ID учителя

    user_manager = UserManager()
    group_data = user_manager.get_group(group_id)
    teacher_data = user_manager.get_user_by_id(teacher_id)  # Теперь используем правильный метод

    if not group_data:
        await callback.answer("❌ Группа не найдена")
        return

    if not teacher_data:
        await callback.answer("❌ Учитель не найден")
        return

    # Назначаем учителя на группу
    if user_manager.assign_teacher_to_group(teacher_id, group_id):
        await callback.message.edit_text(
            f"✅ Учитель {teacher_data['full_name']} назначен на группу {group_data['name']}!"
        )
        # Возвращаемся к информации о группе
        await show_group_info(callback.message, group_id)
    else:
        await callback.message.edit_text(
            f"❌ Ошибка при назначении учителя {teacher_data['full_name']} на группу {group_data['name']}!"
        )
        # Все равно возвращаемся к информации о группе
        await show_group_info(callback.message, group_id)

    await callback.answer()


@router.callback_query(F.data.startswith("remove_teacher_"))
async def remove_teacher(callback: CallbackQuery):
    """Удаление учителя из группы (ИСПРАВЛЕННАЯ ВЕРСИЯ)"""
    group_id = int(callback.data.split("_")[2])

    user_manager = UserManager()
    group_data = user_manager.get_group(group_id)

    if not group_data:
        await callback.answer("❌ Группа не найдена")
        return

    # Удаляем учителя из группы (передаем None)
    if user_manager.update_group_teacher(group_id, None):
        await callback.message.edit_text(
            f"✅ Учитель удален из группы {group_data['name']}!"
        )
        # Возвращаемся к информации о группе
        await show_group_info(callback.message, group_id)
    else:
        await callback.message.edit_text(
            f"❌ Ошибка при удалении учителя из группы {group_data['name']}!"
        )
        # Все равно возвращаемся к информации о группе
        await show_group_info(callback.message, group_id)

    await callback.answer()

@router.callback_query(F.data.startswith("add_students_"))
async def add_students(callback: CallbackQuery, state: FSMContext):
    """Добавление учеников в группу"""
    group_id = int(callback.data.split("_")[2])

    # Сохраняем group_id в состоянии для возврата
    await state.update_data(current_group_id=group_id)

    user_manager = UserManager()
    group_data = user_manager.get_group(group_id)
    if not group_data:
        await callback.answer("❌ Группа не найдена")
        return

    # Получаем учеников без групп
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
    """Выбор ученика для добавления в группу (ИСПРАВЛЕННАЯ ВЕРСИЯ)"""
    data_parts = callback.data.split("_")
    group_id = int(data_parts[2])
    student_id = int(data_parts[3])  # Это внутренний ID ученика

    user_manager = UserManager()
    group_data = user_manager.get_group(group_id)
    student_data = user_manager.get_user_by_id(student_id)  # Теперь используем правильный метод

    if not group_data:
        await callback.answer("❌ Группа не найдена", show_alert=True)
        return

    if not student_data:
        await callback.answer("❌ Ученик не найден", show_alert=True)
        return

    # Добавляем ученика в группу
    if user_manager.assign_user_to_group(student_id, group_id):
        await callback.answer(
            f"✅ Ученик {student_data['full_name']} добавлен в группу {group_data['name']}!",
            show_alert=False
        )

        # Обновляем клавиатуру (убираем добавленного ученика)
        students = user_manager.get_students_without_groups()

        if students:
            await callback.message.edit_reply_markup(
                reply_markup=get_students_selection_keyboard(group_id)
            )
        else:
            # Если учеников больше нет, возвращаем к участникам группы
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

    # Проверяем, есть ли ученики в группе
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
        await callback.message.edit_text(
            f"✅ Группа '{group_data['name']}' успешно удалена!"
        )

        # Показываем обновленный список групп
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

    # Возвращаемся к информации о группе
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


# ========== СОЗДАНИЕ ГРУПП ==========

@router.callback_query(F.data.startswith("new_group_"))
async def create_new_group_for_user(callback: CallbackQuery, state: FSMContext):
    """Создание новой группы для пользователя"""
    user_id = int(callback.data.split("_")[2])
    await state.update_data(approving_user_id=user_id)
    await state.set_state(AdminStates.creating_group_for_user)

    await callback.message.edit_text(
        "Введите название для новой группы:"
    )
    await callback.answer()


@router.callback_query(F.data == "create_group")
async def create_group_callback(callback: CallbackQuery, state: FSMContext):
    """Создание группы из меню"""
    await state.set_state(AdminStates.creating_group)
    await callback.message.answer("Введите название для новой группы:")
    await callback.answer()


@router.message(AdminStates.creating_group)
async def process_new_group(message: Message, state: FSMContext):
    """Обработка создания новой группы"""
    group_name = message.text.strip()
    if not group_name:
        await message.answer("❌ Название группы не может быть пустым. Введите название:")
        return

    user_manager = UserManager()

    if user_manager.create_group(group_name):
        await message.answer(f"✅ Группа '{group_name}' создана!")

        # Показываем список групп
        groups = user_manager.get_all_groups()
        await message.answer(
            "🏫 Выберите группу для просмотра:",
            reply_markup=get_groups_selection_keyboard("group_info")
        )
    else:
        await message.answer("❌ Ошибка при создании группы. Возможно, группа с таким названием уже существует.")

    await state.clear()


@router.message(AdminStates.creating_group_for_user)
async def process_new_group_for_user(message: Message, state: FSMContext):
    """Обработка создания новой группы для пользователя (ИСПРАВЛЕННАЯ ВЕРСИЯ)"""
    group_name = message.text.strip()
    data = await state.get_data()
    user_telegram_id = data.get('approving_user_id')  # Это telegram_id

    if not group_name:
        await message.answer("❌ Название группы не может быть пустым. Введите название:")
        return

    user_manager = UserManager()

    # Создаем группу
    if user_manager.create_group(group_name):
        # Получаем ID новой группы
        groups = user_manager.get_all_groups()
        new_group = next((g for g in groups if g['name'] == group_name), None)

        if new_group and user_telegram_id:
            # Получаем данные пользователя
            user_data = user_manager.get_user(user_telegram_id)

            if not user_data:
                await message.answer("❌ Пользователь не найден")
                await state.clear()
                return

            # Подтверждаем пользователя
            user_manager.approve_user(user_telegram_id)

            # Назначаем в группу в зависимости от роли
            if user_data['role'] == 'teacher':
                success = user_manager.assign_teacher_to_group(user_data['id'], new_group['id'])
                action_text = "назначен учителем"
            else:
                success = user_manager.assign_user_to_group(user_data['id'], new_group['id'])
                action_text = "добавлен в"

            if success:
                await message.answer(
                    f"✅ Группа '{group_name}' создана и {user_data['full_name']} {action_text} нее!"
                )
            else:
                await message.answer(
                    f"✅ Группа '{group_name}' создана, но произошла ошибка при назначении {user_data['full_name']}!"
                )
        else:
            await message.answer("❌ Ошибка при создании группы")
    else:
        await message.answer("❌ Ошибка при создании группы. Возможно, группа с таким названием уже существует.")

    await state.clear()

# ========== ОБРАБОТЧИКИ КОМАНД ИЗ КНОПОК ==========

@router.callback_query(F.data == "cmd_sync")
async def cmd_sync_callback(callback: CallbackQuery):
    """Обработка синхронизации из кнопки"""
    user_manager = UserManager()
    user = user_manager.get_user(callback.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        await callback.answer("❌ Доступ запрещен")
        return

    await callback.message.answer("🔄 Начинаю синхронизацию с Google Sheets...")

    sync_manager = SyncManager()
    success = sync_manager.full_sync()

    if success:
        await callback.message.answer("✅ Синхронизация завершена!")
    else:
        await callback.message.answer("❌ Ошибка синхронизации. Проверьте логи.")

    await callback.answer()


@router.callback_query(F.data == "cmd_export")
async def cmd_export_callback(callback: CallbackQuery):
    """Обработка экспорта из кнопки"""
    user_manager = UserManager()
    user = user_manager.get_user(callback.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        await callback.answer("❌ Доступ запрещен")
        return

    await callback.message.answer("📤 Экспортирую данные в Google Sheets...")

    sync_manager = SyncManager()
    sync_manager.sync_users_to_sheets()
    sync_manager.sync_groups_to_sheets()

    await callback.message.answer("✅ Экспорт завершен!")
    await callback.answer()


@router.callback_query(F.data == "cmd_import")
async def cmd_import_callback(callback: CallbackQuery):
    """Обработка импорта из кнопки"""
    user_manager = UserManager()
    user = user_manager.get_user(callback.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        await callback.answer("❌ Доступ запрещен")
        return

    await callback.message.answer("📥 Импортирую данные из Google Sheets...")

    sync_manager = SyncManager()
    success = sync_manager.sync_from_sheets()

    if success:
        await callback.message.answer("✅ Импорт завершен!")
    else:
        await callback.message.answer("❌ Ошибка импорта. Проверьте логи.")

    await callback.answer()


@router.callback_query(F.data == "cmd_creategroup")
async def cmd_creategroup_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка создания группы из кнопки"""
    user_manager = UserManager()
    user = user_manager.get_user(callback.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        await callback.answer("❌ Доступ запрещен")
        return

    await state.set_state(AdminStates.creating_group)
    await callback.message.answer("Введите название для новой группы:")
    await callback.answer()


@router.callback_query(F.data == "full_stats")
async def full_stats_callback(callback: CallbackQuery):
    """Обработка полной статистики"""
    user_manager = UserManager()
    user = user_manager.get_user(callback.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        await callback.answer("❌ Доступ запрещен")
        return

    stats = user_manager.get_system_stats()

    reports_text = (
        "📊 Полная статистика системы:\n\n"
        f"👥 Всего пользователей: {stats['total_users']}\n"
        f"✅ Активных: {stats['active_users']}\n"
        f"⏳ Ожидают подтверждения: {stats['pending_users']}\n\n"
        f"🎒 Учеников: {stats['students_count']}\n"
        f"👨‍🏫 Учителей: {stats['teachers_count']}\n"
        f"🏫 Групп: {stats['groups_count']}\n\n"
        f"📈 Активность: высокая"
    )

    await callback.message.answer(reports_text)
    await callback.answer()


# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

async def show_group_info(message: Message, group_id: int):
    """Показать информацию о группе (используется в нескольких местах)"""
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


# ========== ОБРАБОТКА НЕИЗВЕСТНЫХ СООБЩЕНИЙ ==========

@router.message()
async def unknown_message(message: Message):
    """Обработка неизвестных сообщений"""
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if user and user['role'] == 'admin' and user['status'] == 'active':
        await message.answer(
            "Используйте меню администратора для управления системой:",
            reply_markup=get_admin_keyboard()
        )
    else:
        await message.answer("❌ Доступ запрещен или вы не авторизованы.")