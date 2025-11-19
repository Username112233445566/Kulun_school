from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

from services.user_manager import UserManager
from services.schedule_manager import ScheduleManager
from services.subjects_manager import SubjectsManager
from states.admin import AdminStates

router = Router()

@router.message(F.text == "Управление расписанием")
async def manage_schedule(message: Message):
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'admin' or user['status'] != 'active':
        return await message.answer("Доступ запрещен")

    groups = user_manager.get_all_groups()

    if not groups:
        await message.answer("Нет созданных групп для управления расписанием")
        return

    keyboard = []
    for group in groups:
        keyboard.append([
            InlineKeyboardButton(
                text=group['name'],
                callback_data=f"manage_schedule_{group['id']}"
            )
        ])

    await message.answer(
        "Выберите группу для управления расписанием:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

@router.callback_query(F.data.startswith("manage_schedule_"))
async def manage_group_schedule(callback: CallbackQuery, state: FSMContext):
    group_id = int(callback.data.split("_")[2])

    user_manager = UserManager()
    group = user_manager.get_group(group_id)

    if not group:
        await callback.answer("Группа не найдена")
        return

    schedule_manager = ScheduleManager()
    schedule = schedule_manager.get_group_schedule(group_id)

    schedule_text = f"Расписание группы {group['name']}:\n\n"

    if not schedule:
        schedule_text += "Расписание не настроено\n"
    else:
        days_mapping = {
            'monday': 'Понедельник',
            'tuesday': 'Вторник',
            'wednesday': 'Среда',
            'thursday': 'Четверг',
            'friday': 'Пятница',
            'saturday': 'Суббота',
            'sunday': 'Воскресенье'
        }

        current_day = None
        for item in schedule:
            day_name = days_mapping.get(item['day_of_week'], item['day_of_week'])
            if day_name != current_day:
                schedule_text += f"\n{day_name}:\n"
                current_day = day_name

            teacher_name = item.get('teacher_name', 'Не назначен')
            schedule_text += f"   {item['start_time']}-{item['end_time']} - {item['subject']} ({teacher_name})\n"

    keyboard = [
        [InlineKeyboardButton(text="Добавить занятие", callback_data=f"add_schedule_{group_id}")],
        [InlineKeyboardButton(text="Назад к группам", callback_data="back_to_schedule_management")]
    ]

    await callback.message.edit_text(
        schedule_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("add_schedule_"))
async def add_schedule_item(callback: CallbackQuery, state: FSMContext):
    group_id = int(callback.data.split("_")[2])

    await state.set_state(AdminStates.adding_schedule_day)
    await state.update_data(group_id=group_id)

    days_keyboard = [
        [InlineKeyboardButton(text="Понедельник", callback_data="day_monday")],
        [InlineKeyboardButton(text="Вторник", callback_data="day_tuesday")],
        [InlineKeyboardButton(text="Среда", callback_data="day_wednesday")],
        [InlineKeyboardButton(text="Четверг", callback_data="day_thursday")],
        [InlineKeyboardButton(text="Пятница", callback_data="day_friday")],
        [InlineKeyboardButton(text="Суббота", callback_data="day_saturday")],
        [InlineKeyboardButton(text="Воскресенье", callback_data="day_sunday")]
    ]

    await callback.message.edit_text(
        "Выберите день недели для занятия:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=days_keyboard)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("day_"))
async def process_day_selection(callback: CallbackQuery, state: FSMContext):
    day_of_week = callback.data.replace("day_", "")

    days_mapping = {
        'monday': 'Понедельник',
        'tuesday': 'Вторник',
        'wednesday': 'Среда',
        'thursday': 'Четверг',
        'friday': 'Пятница',
        'saturday': 'Суббота',
        'sunday': 'Воскресенье'
    }

    day_name = days_mapping.get(day_of_week, day_of_week)

    await state.update_data(day_of_week=day_of_week)
    await state.set_state(AdminStates.adding_schedule_time)

    await callback.message.edit_text(
        f"Выбран день: {day_name}\n\n"
        "Введите время занятия в формате:\n"
        "ЧЧ:ММ-ЧЧ:ММ\n\n"
        "Например: 14:00-15:30"
    )
    await callback.answer()

@router.message(AdminStates.adding_schedule_time)
async def process_time_input(message: Message, state: FSMContext):
    time_input = message.text.strip()

    if not ("-" in time_input and ":" in time_input):
        await message.answer(
            "Неверный формат времени. Используйте формат:\n"
            "ЧЧ:ММ-ЧЧ:ММ\n\n"
            "Например: 14:00-15:30\n"
            "Попробуйте еще раз:"
        )
        return

    try:
        start_time, end_time = time_input.split("-")
        start_hour, start_minute = map(int, start_time.split(":"))
        end_hour, end_minute = map(int, end_time.split(":"))

        if not (0 <= start_hour <= 23 and 0 <= start_minute <= 59 and
                0 <= end_hour <= 23 and 0 <= end_minute <= 59):
            raise ValueError

    except (ValueError, AttributeError):
        await message.answer(
            "Неверный формат времени. Используйте формат:\n"
            "ЧЧ:ММ-ЧЧ:ММ\n\n"
            "Например: 14:00-15:30\n"
            "Попробуйте еще раз:"
        )
        return

    await state.update_data(start_time=start_time.strip(), end_time=end_time.strip())
    await state.set_state(AdminStates.adding_schedule_subject)

    subjects_manager = SubjectsManager()
    subjects = subjects_manager.get_all_subjects()

    if subjects:
        keyboard = []
        for subject in subjects:
            keyboard.append([
                InlineKeyboardButton(
                    text=subject['name'],
                    callback_data=f"subject_{subject['id']}"
                )
            ])
        keyboard.append([InlineKeyboardButton(text="Ввести вручную", callback_data="subject_manual")])

        await message.answer(
            "Выберите предмет из списка или введите вручную:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
    else:
        await message.answer("Введите название предмета для занятия:")

@router.callback_query(F.data.startswith("subject_"))
async def process_subject_selection(callback: CallbackQuery, state: FSMContext):
    subject_data = callback.data.replace("subject_", "")

    if subject_data == "manual":
        await state.set_state(AdminStates.adding_schedule_subject)
        await callback.message.edit_text("Введите название предмета для занятия:")
        await callback.answer()
        return

    subjects_manager = SubjectsManager()
    subject = subjects_manager.get_subject(int(subject_data))

    if subject:
        await state.update_data(subject=subject['name'])
        await complete_schedule_creation(callback.message, state)
    else:
        await callback.message.edit_text("Предмет не найден. Введите название предмета:")
        await state.set_state(AdminStates.adding_schedule_subject)

    await callback.answer()

@router.message(AdminStates.adding_schedule_subject)
async def process_subject_input(message: Message, state: FSMContext):
    subject_name = message.text.strip()

    if not subject_name:
        await message.answer("Название предмета не может быть пустым. Введите название:")
        return

    await state.update_data(subject=subject_name)
    await complete_schedule_creation(message, state)

async def complete_schedule_creation(message: Message, state: FSMContext):
    data = await state.get_data()

    group_id = data.get('group_id')
    day_of_week = data.get('day_of_week')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    subject = data.get('subject')

    if not all([group_id, day_of_week, start_time, end_time, subject]):
        await message.answer("Ошибка: Не все данные заполнены. Пожалуйста, начните заново.")
        await state.clear()
        return

    schedule_manager = ScheduleManager()
    success = schedule_manager.add_schedule_item(
        group_id=group_id,
        day_of_week=day_of_week,
        start_time=start_time,
        end_time=end_time,
        subject=subject
    )

    if success:
        days_mapping = {
            'monday': 'Понедельник',
            'tuesday': 'Вторник',
            'wednesday': 'Среда',
            'thursday': 'Четверг',
            'friday': 'Пятница',
            'saturday': 'Суббота',
            'sunday': 'Воскресенье'
        }

        day_name = days_mapping.get(day_of_week, day_of_week)

        await message.answer(
            f"Занятие успешно добавлено!\n\n"
            f"День: {day_name}\n"
            f"Время: {start_time}-{end_time}\n"
            f"Предмет: {subject}"
        )

        await show_updated_schedule(message, group_id)
    else:
        await message.answer("Ошибка при добавлении занятия. Попробуйте еще раз.")

    await state.clear()

async def show_updated_schedule(message: Message, group_id: int):
    user_manager = UserManager()
    schedule_manager = ScheduleManager()

    group = user_manager.get_group(group_id)
    schedule = schedule_manager.get_group_schedule(group_id)

    schedule_text = f"Расписание группы {group['name']}:\n\n"

    if not schedule:
        schedule_text += "Расписание не настроено\n"
    else:
        days_mapping = {
            'monday': 'Понедельник',
            'tuesday': 'Вторник',
            'wednesday': 'Среда',
            'thursday': 'Четверг',
            'friday': 'Пятница',
            'saturday': 'Суббота',
            'sunday': 'Воскресенье'
        }

        current_day = None
        for item in schedule:
            day_name = days_mapping.get(item['day_of_week'], item['day_of_week'])
            if day_name != current_day:
                schedule_text += f"\n{day_name}:\n"
                current_day = day_name

            teacher_name = item.get('teacher_name', 'Не назначен')
            schedule_text += f"   {item['start_time']}-{item['end_time']} - {item['subject']} ({teacher_name})\n"

    keyboard = [
        [InlineKeyboardButton(text="Добавить занятие", callback_data=f"add_schedule_{group_id}")],
        [InlineKeyboardButton(text="Назад к группам", callback_data="back_to_schedule_management")]
    ]

    await message.answer(
        schedule_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

@router.callback_query(F.data == "back_to_schedule_management")
async def back_to_schedule_management(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await manage_schedule(callback.message)
    await callback.answer()