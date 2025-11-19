from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Пользователи"), KeyboardButton(text="Группы")],
            [KeyboardButton(text="Предметы"), KeyboardButton(text="Управление расписанием")],
            [KeyboardButton(text="Отчеты"), KeyboardButton(text="Синхронизация")]
        ],
        resize_keyboard=True
    )

def get_reports_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Экспорт", callback_data="cmd_export"),
                InlineKeyboardButton(text="Импорт", callback_data="cmd_import")
            ],
            [
                InlineKeyboardButton(text="Общая статистика", callback_data="full_stats")
            ]
        ]
    )