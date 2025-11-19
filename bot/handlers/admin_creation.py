from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.keyboards.admin import get_groups_selection_keyboard
from services.user_manager import UserManager
from states.admin import AdminStates

router = Router()

@router.message(Command("creategroup"))
async def cmd_create_group(message: Message, state: FSMContext):
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        return await message.answer("Доступ запрещен")

    await state.set_state(AdminStates.creating_group)
    await message.answer("Введите название для новой группы:")

@router.message(F.text == "Создать группу")
async def create_group_button(message: Message, state: FSMContext):
    await cmd_create_group(message, state)

@router.callback_query(F.data.startswith("new_group_"))
async def create_new_group_for_user(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split("_")[2])
    await state.update_data(approving_user_id=user_id)
    await state.set_state(AdminStates.creating_group_for_user)

    await callback.message.edit_text("Введите название для новой группы:")
    await callback.answer()

@router.callback_query(F.data == "create_group")
async def create_group_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.creating_group)
    await callback.message.answer("Введите название для новой группы:")
    await callback.answer()

@router.message(AdminStates.creating_group)
async def process_new_group(message: Message, state: FSMContext):
    group_name = message.text.strip()
    if not group_name:
        await message.answer("Название группы не может быть пустым. Введите название:")
        return

    user_manager = UserManager()

    if user_manager.create_group(group_name):
        await message.answer(f"Группа '{group_name}' создана!")

        groups = user_manager.get_all_groups()
        await message.answer(
            "Выберите группу для просмотра:",
            reply_markup=get_groups_selection_keyboard("group_info")
        )
    else:
        await message.answer("Ошибка при создании группы. Возможно, группа с таким названием уже существует.")

    await state.clear()

@router.message(AdminStates.creating_group_for_user)
async def process_new_group_for_user(message: Message, state: FSMContext):
    group_name = message.text.strip()
    data = await state.get_data()
    user_telegram_id = data.get('approving_user_id')

    if not group_name:
        await message.answer("Название группы не может быть пустым. Введите название:")
        return

    user_manager = UserManager()

    if user_manager.create_group(group_name):
        groups = user_manager.get_all_groups()
        new_group = next((g for g in groups if g['name'] == group_name), None)

        if new_group and user_telegram_id:
            user_data = user_manager.get_user(user_telegram_id)

            if not user_data:
                await message.answer("Пользователь не найден")
                await state.clear()
                return

            user_manager.approve_user(user_telegram_id)

            if user_data['role'] == 'teacher':
                success = user_manager.assign_teacher_to_group(user_data['id'], new_group['id'])
                action_text = "назначен учителем"
            else:
                success = user_manager.assign_user_to_group(user_data['id'], new_group['id'])
                action_text = "добавлен в"

            if success:
                await message.answer(
                    f"Группа '{group_name}' создана и {user_data['full_name']} {action_text} нее!"
                )
            else:
                await message.answer(
                    f"Группа '{group_name}' создана, но произошла ошибка при назначении {user_data['full_name']}!"
                )
        else:
            await message.answer("Ошибка при создании группы")
    else:
        await message.answer("Ошибка при создании группы. Возможно, группа с таким названием уже существует.")

    await state.clear()

@router.callback_query(F.data == "cmd_creategroup")
async def cmd_creategroup_callback(callback: CallbackQuery, state: FSMContext):
    user_manager = UserManager()
    user = user_manager.get_user(callback.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        await callback.answer("Доступ запрещен")
        return

    await state.set_state(AdminStates.creating_group)
    await callback.message.answer("Введите название для новой группы:")
    await callback.answer()