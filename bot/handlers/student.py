from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from bot.keyboards.student import get_student_keyboard
from services.user_manager import UserManager

router = Router()


@router.message(F.text == "📅 Расписание")
async def student_schedule(message: Message):
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'student':
        return await message.answer("❌ Доступ запрещен")

    schedule_text = "📅 Ваше расписание:\n\nПонедельник: 10:00 - Английский\nВторник: 11:00 - Математика"
    await message.answer(schedule_text)


@router.message(F.text == "📝 Мои задания")
async def student_assignments(message: Message):
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'student':
        return await message.answer("❌ Доступ запрещен")

    # Получаем задания из Google Sheets
    assignments = user_manager.get_assignments_for_student(user['group'])

    if not assignments:
        await message.answer("📭 У вас пока нет заданий")
        return

    assignments_text = "📚 Ваши задания:\n\n"
    for assignment in assignments:
        assignments_text += f"📖 {assignment['title']}\n"
        assignments_text += f"📝 {assignment['description']}\n"
        assignments_text += f"⏰ До: {assignment['deadline']}\n\n"

    await message.answer(assignments_text)


@router.message(F.text == "📊 Мои результаты")
async def student_results(message: Message):
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'student':
        return await message.answer("❌ Доступ запрещен")

    results_text = (
        "📊 Ваши результаты:\n\n"
        "📈 Посещаемость: 95%\n"
        "⭐ Средний балл: 4.8\n"
        "✅ Выполнено заданий: 15\n"
        "🎯 Прогресс: Отлично!"
    )
    await message.answer(results_text)


@router.message(F.text == "👤 Мой профиль")
async def student_profile(message: Message):
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'student':
        return await message.answer("❌ Доступ запрещен")

    profile_text = (
        f"👤 Ваш профиль:\n\n"
        f"🎒 Имя: {user['full_name']}\n"
        f"📞 Телефон: {user['phone']}\n"
        f"🏫 Группа: {user['group']}\n"
        f"📅 Дата регистрации: {user['created_at']}"
    )
    await message.answer(profile_text)