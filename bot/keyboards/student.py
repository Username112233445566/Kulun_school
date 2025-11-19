from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_student_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Расписание"), KeyboardButton(text="Мои задания")],
            [KeyboardButton(text="Мои результаты"), KeyboardButton(text="Мой профиль")]
        ],
        resize_keyboard=True
    )