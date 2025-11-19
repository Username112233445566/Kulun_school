from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from services.subjects_manager import SubjectsManager
from services.user_manager import UserManager
from states.admin import AdminStates
from bot.keyboards.admin import get_subjects_management_keyboard, get_confirmation_keyboard

router = Router()

@router.message(Command("subjects"))
async def manage_subjects(message: Message):
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        return await message.answer("Доступ запрещен")

    subjects_manager = SubjectsManager()
    subjects = subjects_manager.get_all_subjects()

    if not subjects:
        await message.answer(
            "Нет добавленных предметов\n\n"
            "Хотите добавить первый предмет?",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Добавить предмет", callback_data="add_subject")],
                    [InlineKeyboardButton(text="Назад", callback_data="back_to_admin_menu")]
                ]
            )
        )
        return

    subjects_text = "Список предметов:\n\n"
    for subject in subjects:
        subjects_text += f"{subject['id']}. {subject['name']}"
        if subject.get('description'):
            subjects_text += f" - {subject['description']}"
        subjects_text += "\n"

    await message.answer(
        subjects_text,
        reply_markup=get_subjects_management_keyboard()
    )

@router.message(F.text == "Предметы")
async def subjects_button(message: Message):
    await manage_subjects(message)

@router.callback_query(F.data == "add_subject")
async def add_subject_callback(callback: CallbackQuery, state: FSMContext):
    user_manager = UserManager()
    user = user_manager.get_user(callback.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        await callback.answer("Доступ запрещен")
        return

    await state.set_state(AdminStates.adding_subject_name)
    await callback.message.answer("Введите название нового предмета:")
    await callback.answer()

@router.message(AdminStates.adding_subject_name)
async def process_subject_name(message: Message, state: FSMContext):
    subject_name = message.text.strip()

    if not subject_name:
        await message.answer("Название предмета не может быть пустым. Введите название:")
        return

    await state.update_data(subject_name=subject_name)
    await state.set_state(AdminStates.adding_subject_description)

    await message.answer("Введите описание предмета (или отправьте '-' чтобы пропустить):")

@router.message(AdminStates.adding_subject_description)
async def process_subject_description(message: Message, state: FSMContext):
    description = message.text.strip()
    if description == "-":
        description = None

    data = await state.get_data()
    subject_name = data['subject_name']

    subjects_manager = SubjectsManager()

    if subjects_manager.add_subject(subject_name, description):
        await message.answer(f"Предмет '{subject_name}' успешно добавлен!")
    else:
        await message.answer("Ошибка при добавлении предмета. Возможно, предмет с таким названием уже существует.")

    await state.clear()

@router.callback_query(F.data == "view_subjects")
async def view_subjects_callback(callback: CallbackQuery):
    user_manager = UserManager()
    user = user_manager.get_user(callback.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        await callback.answer("Доступ запрещен")
        return

    subjects_manager = SubjectsManager()
    subjects = subjects_manager.get_all_subjects()

    if not subjects:
        await callback.message.edit_text("Нет добавленных предметов")
        await callback.answer()
        return

    subjects_text = "Список предметов:\n\n"
    for subject in subjects:
        subjects_text += f"{subject['id']}. {subject['name']}"
        if subject.get('description'):
            subjects_text += f" - {subject['description']}"
        subjects_text += "\n"

    await callback.message.edit_text(subjects_text)
    await callback.answer()

@router.callback_query(F.data.startswith("delete_subject_"))
async def delete_subject_confirmation(callback: CallbackQuery):
    subject_id = int(callback.data.split("_")[2])

    user_manager = UserManager()
    user = user_manager.get_user(callback.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        await callback.answer("Доступ запрещен")
        return

    subjects_manager = SubjectsManager()
    subject = subjects_manager.get_subject(subject_id)

    if not subject:
        await callback.answer("Предмет не найден")
        return

    await callback.message.edit_text(
        f"Вы уверены, что хотите удалить предмет '{subject['name']}'?",
        reply_markup=get_confirmation_keyboard("delete_subject", subject_id)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("confirm_delete_subject_"))
async def confirm_delete_subject(callback: CallbackQuery):
    subject_id = int(callback.data.split("_")[3])

    user_manager = UserManager()
    user = user_manager.get_user(callback.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        await callback.answer("Доступ запрещен")
        return

    subjects_manager = SubjectsManager()
    subject = subjects_manager.get_subject(subject_id)

    if not subject:
        await callback.answer("Предмет не найден")
        return

    if subjects_manager.delete_subject(subject_id):
        await callback.message.edit_text(f"Предмет '{subject['name']}' успешно удален!")
    else:
        await callback.message.edit_text("Ошибка при удалении предмета.")

    await callback.answer()

@router.callback_query(F.data.startswith("cancel_delete_subject_"))
async def cancel_delete_subject(callback: CallbackQuery):
    await callback.message.edit_text("Удаление предмета отменено.")
    await callback.answer()

@router.callback_query(F.data == "back_to_admin_menu")
async def back_to_admin_menu(callback: CallbackQuery):
    from bot.keyboards.admin import get_admin_keyboard

    user_manager = UserManager()
    user = user_manager.get_user(callback.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        await callback.answer("Доступ запрещен")
        return

    await callback.message.edit_text(
        "Панель администратора",
        reply_markup=get_admin_keyboard()
    )
    await callback.answer()