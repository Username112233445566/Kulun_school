from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_role_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎒 Ученик")],
            [KeyboardButton(text="👨‍🏫 Учитель")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_phone_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Отправить номер", request_contact=True)],
            [KeyboardButton(text="✏️ Ввести вручную")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )