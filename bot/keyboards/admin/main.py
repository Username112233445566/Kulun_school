from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_keyboard():
    """Основная клавиатура администратора"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 Подтверждение"), KeyboardButton(text="🏫 Группы")],
            [KeyboardButton(text="📚 Предметы"), KeyboardButton(text="📅 Управление расписанием")],
            [KeyboardButton(text="📊 Отчеты"), KeyboardButton(text="🔄 Синхронизация")],
            [KeyboardButton(text="➕ Создать группу")]
        ],
        resize_keyboard=True
    )

def get_reports_keyboard():
    """Клавиатура для раздела отчетов"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📤 Экспорт", callback_data="cmd_export"),
                InlineKeyboardButton(text="📥 Импорт", callback_data="cmd_import")
            ],
            [
                InlineKeyboardButton(text="📊 Общая статистика", callback_data="full_stats")
            ]
        ]
    )