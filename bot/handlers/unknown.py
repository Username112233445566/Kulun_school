from aiogram import Router
from aiogram.types import Message
from bot.keyboards.admin import get_admin_keyboard
from services.user_manager import UserManager

router = Router()

@router.message()
async def unknown_message(message: Message):
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user:
        await message.answer("Вы не зарегистрированы в системе. Используйте /start")
        return

    if user['role'] == 'admin' and user['status'] == 'active':
        await message.answer(
            f"Команда '{message.text}' не распознана. Используйте меню администратора:",
            reply_markup=get_admin_keyboard()
        )
    elif user['role'] == 'teacher' and user['status'] == 'active':
        from bot.keyboards.teacher import get_teacher_keyboard
        await message.answer(
            f"Команда '{message.text}' не распознана. Используйте меню учителя:",
            reply_markup=get_teacher_keyboard()
        )
    elif user['role'] == 'student' and user['status'] == 'active':
        from bot.keyboards.student import get_student_keyboard
        await message.answer(
            f"Команда '{message.text}' не распознана. Используйте меню ученика:",
            reply_markup=get_student_keyboard()
        )
    else:
        await message.answer("Доступ запрещен или вы не авторизованы.")