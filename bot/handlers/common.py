from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.keyboards.common import get_role_keyboard, get_phone_keyboard
from bot.keyboards.student import get_student_keyboard
from bot.keyboards.teacher import get_teacher_keyboard
from bot.keyboards.admin import get_admin_keyboard
from states.registration import RegistrationStates
from services.user_manager import UserManager

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if user:
        if user['status'] == 'pending':
            await message.answer("Ваша заявка на рассмотрении. Ожидайте подтверждения администратора.")
            return

        if user['role'] == 'student':
            await message.answer("Добро пожаловать!", reply_markup=get_student_keyboard())
        elif user['role'] == 'teacher':
            await message.answer("Добро пожаловать!", reply_markup=get_teacher_keyboard())
        elif user['role'] == 'admin':
            await message.answer("Панель администратора", reply_markup=get_admin_keyboard())
        return
    else:
        await state.set_state(RegistrationStates.choosing_role)
        await message.answer(
            "Добро пожаловать! Выберите вашу роль:",
            reply_markup=get_role_keyboard()
        )

@router.message(RegistrationStates.choosing_role, F.text.in_(["Ученик", "Учитель"]))
async def process_role_choice(message: Message, state: FSMContext):
    role_map = {
        "Ученик": "student",
        "Учитель": "teacher"
    }

    role = role_map[message.text]
    await state.update_data(role=role)
    await state.set_state(RegistrationStates.entering_name)

    await message.answer(
        "Введите ваше ФИО:",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(RegistrationStates.entering_name)
async def process_name(message: Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 2:
        await message.answer("Имя должно содержать хотя бы 2 символа. Введите ваше ФИО:")
        return

    await state.update_data(full_name=message.text.strip())
    await state.set_state(RegistrationStates.entering_phone)

    await message.answer(
        "Введите ваш номер телефона:",
        reply_markup=get_phone_keyboard()
    )

@router.message(RegistrationStates.entering_phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext):
    if not message.contact or not message.contact.phone_number:
        await message.answer("Не удалось получить номер телефона. Попробуйте еще раз:")
        return

    phone = message.contact.phone_number
    if not phone.startswith('+'):
        phone = '+' + phone

    await state.update_data(phone=phone)
    await complete_registration(message, state)

@router.message(RegistrationStates.entering_phone, F.text)
async def process_phone_text(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Введите номер телефона:")
        return

    phone = message.text.strip()
    digits = ''.join(filter(str.isdigit, phone))
    if len(digits) < 10:
        await message.answer("Введите корректный номер телефона (минимум 10 цифр):")
        return

    if not phone.startswith('+'):
        if phone.startswith('8'):
            phone = '+7' + phone[1:]
        elif phone.startswith('7'):
            phone = '+' + phone
        else:
            phone = '+7' + phone

    await state.update_data(phone=phone)
    await complete_registration(message, state)

async def complete_registration(message: Message, state: FSMContext):
    user_data = await state.get_data()
    user_manager = UserManager()

    if not all(key in user_data for key in ['role', 'full_name', 'phone']):
        await message.answer("Произошла ошибка при регистрации. Попробуйте снова: /start")
        await state.clear()
        return

    user = user_manager.create_user(
        telegram_id=message.from_user.id,
        full_name=user_data['full_name'],
        phone=user_data['phone'],
        role=user_data['role']
    )

    await state.clear()

    role_display = "Ученик" if user_data['role'] == 'student' else "Учитель"

    await message.answer(
        "Заявка отправлена! Ожидайте подтверждения администратора.\n\n"
        f"Ваши данные:\n"
        f"ФИО: {user_data['full_name']}\n"
        f"Телефон: {user_data['phone']}\n"
        f"Роль: {role_display}",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "Помощь по боту KULUN School\n\n"
        "Основные команды:\n"
        "/start - начать работу\n"
        "/help - эта справка\n\n"
        "Если у вас возникли проблемы, обратитесь к администратору."
    )
    await message.answer(help_text)