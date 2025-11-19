from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_approval_keyboard(user_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Подтвердить", callback_data=f"approve_{user_id}"),
                InlineKeyboardButton(text="Отклонить", callback_data=f"reject_{user_id}")
            ]
        ]
    )