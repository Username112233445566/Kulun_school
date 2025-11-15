from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards.teacher import get_teacher_keyboard
from services.user_manager import UserManager
from states.attendance import AttendanceStates
from states.assignments import AssignmentStates

router = Router()


@router.message(F.text == "👥 Мои группы")
async def teacher_groups(message: Message):
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'teacher':
        return await message.answer("❌ Доступ запрещен")

    groups = user_manager.get_teacher_groups(user['id'])

    if not groups:
        await message.answer("📭 У вас пока нет групп")
        return

    groups_text = "👥 Ваши группы:\n\n"
    for group in groups:
        groups_text += f"🏫 {group['name']}\n"
        groups_text += f"👨‍🎓 Учеников: {group['students_count']}\n\n"

    await message.answer(groups_text)


@router.message(F.text == "✅ Посещаемость")
async def teacher_attendance(message: Message, state: FSMContext):
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'teacher':
        return await message.answer("❌ Доступ запрещен")

    await state.set_state(AttendanceStates.choosing_group)
    await message.answer("Выберите группу для отметки посещаемости:")


@router.message(F.text == "📝 Создать задание")
async def teacher_create_assignment(message: Message, state: FSMContext):
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'teacher':
        return await message.answer("❌ Доступ запрещен")

    await state.set_state(AssignmentStates.choosing_group)
    await message.answer("Выберите группу для задания:")


@router.message(F.text == "📊 Успеваемость")
async def teacher_performance(message: Message):
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'teacher':
        return await message.answer("❌ Доступ запрещен")

    performance_text = (
        "📊 Успеваемость групп:\n\n"
        "🏫 Group A:\n"
        "  📈 Средний балл: 4.5\n"
        "  ✅ Посещаемость: 92%\n"
        "  👥 Учеников: 15\n\n"
        "🏫 Group B:\n"
        "  📈 Средний балл: 4.2\n"
        "  ✅ Посещаемость: 88%\n"
        "  👥 Учеников: 12"
    )
    await message.answer(performance_text)