from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict


def get_admin_keyboard():
    """Основная клавиатура администратора"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 Подтверждение"), KeyboardButton(text="🏫 Группы")],
            [KeyboardButton(text="📊 Отчеты")],
            [KeyboardButton(text="🔄 Синхронизация"), KeyboardButton(text="📤 Экспорт")],
            [KeyboardButton(text="📥 Импорт"), KeyboardButton(text="➕ Создать группу")]
        ],
        resize_keyboard=True
    )


def get_approval_keyboard(user_id: int):
    """Клавиатура для подтверждения пользователя"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"approve_{user_id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{user_id}")
            ]
        ]
    )


def get_groups_selection_keyboard(action: str, user_id: int = None):
    """Клавиатура для выбора группы"""
    from services.user_manager import UserManager
    user_manager = UserManager()
    groups = user_manager.get_all_groups()

    keyboard = []
    for group in groups:
        if user_id:
            callback_data = f"{action}_{user_id}_{group['id']}"
        else:
            callback_data = f"{action}_{group['id']}"

        keyboard.append([
            InlineKeyboardButton(
                text=f"🏫 {group['name']}",
                callback_data=callback_data
            )
        ])

    # Кнопка для создания новой группы
    if user_id:
        keyboard.append([
            InlineKeyboardButton(
                text="➕ Создать новую группу",
                callback_data=f"new_group_{user_id}"
            )
        ])
    else:
        keyboard.append([
            InlineKeyboardButton(
                text="➕ Создать новую группу",
                callback_data="create_group"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_group_management_keyboard(group_id: int):
    """Клавиатура для управления группой"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👥 Участники", callback_data=f"group_members_{group_id}"),
                InlineKeyboardButton(text="✏️ Изменить название", callback_data=f"edit_group_name_{group_id}")
            ],
            [
                InlineKeyboardButton(text="👨‍🏫 Назначить учителя", callback_data=f"assign_teacher_{group_id}"),
                InlineKeyboardButton(text="🎒 Добавить учеников", callback_data=f"add_students_{group_id}")
            ],
            [
                InlineKeyboardButton(text="📊 Статистика", callback_data=f"group_stats_{group_id}"),
                InlineKeyboardButton(text="🗑️ Удалить группу", callback_data=f"delete_group_{group_id}")
            ],
            [
                InlineKeyboardButton(text="🔙 Назад к списку", callback_data="back_to_groups")
            ]
        ]
    )


def get_group_members_management_keyboard(group_id: int):
    """Клавиатура для управления участниками группы"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎒 Управление учениками", callback_data=f"manage_students_{group_id}"),
                InlineKeyboardButton(text="👨‍🏫 Назначить учителя", callback_data=f"assign_teacher_{group_id}")
            ],
            [
                InlineKeyboardButton(text="🔙 Назад к группе", callback_data=f"group_info_{group_id}")
            ]
        ]
    )


def get_students_management_keyboard(group_id: int, students: List[Dict]):
    """Клавиатура для управления учениками в группе"""
    keyboard = []

    for student in students:
        keyboard.append([
            InlineKeyboardButton(
                text=f"❌ {student['full_name']}",
                callback_data=f"remove_student_{group_id}_{student['id']}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(text="🎒 Добавить учеников", callback_data=f"add_students_{group_id}"),
        InlineKeyboardButton(text="🔙 Назад", callback_data=f"group_members_{group_id}")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_teachers_selection_keyboard(group_id: int):
    """Клавиатура для выбора учителя"""
    from services.user_manager import UserManager
    user_manager = UserManager()
    teachers = user_manager.get_available_teachers()  # Теперь этот метод существует

    keyboard = []
    for teacher in teachers:
        keyboard.append([
            InlineKeyboardButton(
                text=f"👨‍🏫 {teacher['full_name']}",
                callback_data=f"select_teacher_{group_id}_{teacher['id']}"
            )
        ])

    # Получаем текущего учителя группы
    current_group = user_manager.get_group(group_id)
    if current_group and current_group.get('teacher_id'):
        keyboard.append([
            InlineKeyboardButton(text="❌ Удалить текущего учителя", callback_data=f"remove_teacher_{group_id}")
        ])

    keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data=f"group_info_{group_id}")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_students_selection_keyboard(group_id: int):
    """Клавиатура для выбора учеников (ИСПРАВЛЕННАЯ ВЕРСИЯ)"""
    from services.user_manager import UserManager
    user_manager = UserManager()
    students = user_manager.get_students_without_groups()

    keyboard = []
    for student in students:
        keyboard.append([
            InlineKeyboardButton(
                text=f"🎒 {student['full_name']}",
                callback_data=f"select_student_{group_id}_{student['id']}"  # Используем внутренний ID
            )
        ])

    if not students:
        keyboard.append([
            InlineKeyboardButton(text="📭 Нет доступных учеников", callback_data="no_action")
        ])

    keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data=f"group_members_{group_id}")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_confirmation_keyboard(action: str, item_id: int):
    """Клавиатура для подтверждения действий"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_{action}_{item_id}"),
                InlineKeyboardButton(text="❌ Нет", callback_data=f"cancel_{action}_{item_id}")
            ]
        ]
    )


def get_reports_keyboard():
    """Клавиатура для раздела отчетов"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 Синхронизировать", callback_data="cmd_sync"),
                InlineKeyboardButton(text="📤 Экспорт в Sheets", callback_data="cmd_export")
            ],
            [
                InlineKeyboardButton(text="📥 Импорт из Sheets", callback_data="cmd_import"),
                InlineKeyboardButton(text="➕ Создать группу", callback_data="cmd_creategroup")
            ],
            [
                InlineKeyboardButton(text="📊 Общая статистика", callback_data="full_stats")
            ]
        ]
    )