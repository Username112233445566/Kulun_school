from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_teacher_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👥 Мои группы"), KeyboardButton(text="✅ Посещаемость")],
            [KeyboardButton(text="📝 Создать задание"), KeyboardButton(text="📊 Успеваемость")]
        ],
        resize_keyboard=True
    )