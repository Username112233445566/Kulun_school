from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from services.grades_manager import GradesManager
from services.attendance_manager import AttendanceManager

from services.assignment_manager import AssignmentManager
from services.user_manager import UserManager
from services.schedule_manager import ScheduleManager

router = Router()


@router.message(F.text == "📅 Расписание")
async def student_schedule(message: Message):
    """Показывает реальное расписание ученика"""
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'student' or user['status'] != 'active':
        return await message.answer("❌ Доступ запрещен")

    if not user.get('group_id'):
        await message.answer(
            "📭 У вас нет назначенной группы.\n\n"
            "Обратитесь к администратору для назначения в группу."
        )
        return

    schedule_manager = ScheduleManager()
    schedule = schedule_manager.get_group_schedule(user['group_id'])

    # Получаем информацию о группе
    group = user_manager.get_group(user['group_id'])
    group_name = group['name'] if group else "Неизвестная группа"

    schedule_text = f"📅 Расписание группы {group_name}:\n\n"

    if not schedule:
        schedule_text += (
            "📭 Расписание еще не настроено\n\n"
            "Обратитесь к администратору для настройки расписания."
        )
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
                schedule_text += f"\n📌 **{day_name}**:\n"
                current_day = day_name

            teacher_name = item.get('teacher_name', 'Преподаватель не назначен')
            schedule_text += f"   🕐 {item['start_time']}-{item['end_time']}\n"
            schedule_text += f"   📚 {item['subject']}\n"
            schedule_text += f"   👨‍🏫 {teacher_name}\n\n"

    await message.answer(schedule_text)

@router.message(F.text == "📝 Мои задания")
async def student_assignments(message: Message):
    """Показывает задания ученика с реальными данными"""
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'student' or user['status'] != 'active':
        return await message.answer("❌ Доступ запрещен")

    # Проверяем, есть ли у ученика группа - ИСПРАВЛЕННАЯ ВЕРСИЯ
    if not user.get('group_id'):
        await message.answer(
            "📭 У вас нет назначенной группы.\n\n"
            "Обратитесь к администратору для назначения в группу."
        )
        return

    assignment_manager = AssignmentManager()
    assignments = assignment_manager.get_assignments_for_student(user['id'])  # Используем user['id']

    if not assignments:
        await message.answer(
            "📭 У вас пока нет заданий\n\n"
            "Задания появятся здесь, когда учитель их создаст."
        )
        return

    assignments_text = "📚 Ваши задания:\n\n"

    for i, assignment in enumerate(assignments, 1):
        assignments_text += f"{i}. 🔹 **{assignment['title']}**\n"

        if assignment.get('description'):
            assignments_text += f"   📝 {assignment['description']}\n"

        if assignment.get('deadline'):
            # Форматируем дату
            deadline = assignment['deadline']
            if isinstance(deadline, str):
                assignments_text += f"   ⏰ До: {deadline}\n"
            else:
                assignments_text += f"   ⏰ До: {deadline.strftime('%d.%m.%Y')}\n"

        if assignment.get('teacher_name'):
            assignments_text += f"   👨‍🏫 Преподаватель: {assignment['teacher_name']}\n"

        assignments_text += "\n"

    assignments_text += f"📊 Всего заданий: {len(assignments)}"

    await message.answer(assignments_text)


@router.message(F.text == "📊 Мои результаты")
async def student_results(message: Message):
    """Показывает реальные результаты ученика"""
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'student' or user['status'] != 'active':
        return await message.answer("❌ Доступ запрещен")

    if not user.get('group_id'):
        await message.answer("📭 У вас нет группы для отображения результатов")
        return

    grades_manager = GradesManager()
    attendance_manager = AttendanceManager()

    try:
        # Получаем реальные данные
        average_grade = grades_manager.get_average_grade(user['id'])
        attendance_stats = attendance_manager.get_student_attendance_stats(user['id'], user['group_id'])

        # Получаем последние оценки
        recent_grades = grades_manager.get_student_grades(user['id'])[:5]

        # Получаем статистику по предметам
        all_grades = grades_manager.get_student_grades(user['id'])
        subjects_grades = {}

        for grade in all_grades:
            subject = grade['subject']
            if subject not in subjects_grades:
                subjects_grades[subject] = []
            subjects_grades[subject].append(grade['grade'])

        # Формируем текст результатов
        results_text = f"📊 Ваши результаты, {user['full_name']}:\n\n"

        # Статистика посещаемости
        results_text += f"📈 Посещаемость: {attendance_stats.get('attendance_rate', 0)}%\n"
        results_text += f"🎯 Всего занятий: {attendance_stats.get('total_classes', 0)}\n"
        results_text += f"✅ Присутствовал: {attendance_stats.get('present', 0)}\n\n"

        # Средний балл
        results_text += f"⭐ Средний балл: {average_grade:.1f}\n"
        results_text += f"📝 Всего оценок: {len(all_grades)}\n\n"

        # Оценки по предметам
        if subjects_grades:
            results_text += "📚 Оценки по предметам:\n"
            for subject, grades in subjects_grades.items():
                subject_avg = sum(grades) / len(grades)
                results_text += f"   {subject}: {subject_avg:.1f} ({len(grades)} оценок)\n"
            results_text += "\n"

        # Последние оценки
        if recent_grades:
            results_text += "📋 Последние оценки:\n"
            for grade in recent_grades:
                results_text += f"   {grade['subject']}: {grade['grade']} ({grade['date']})\n"

        await message.answer(results_text)

    except Exception as e:
        logger.error(f"❌ Ошибка при получении результатов: {e}")
        await message.answer(
            "❌ Не удалось загрузить результаты.\n"
            "Попробуйте позже или обратитесь к администратору."
        )


@router.message(F.text == "👤 Мой профиль")
async def student_profile(message: Message):
    """Показывает профиль ученика с расширенной информацией"""
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'student':
        return await message.answer("❌ Доступ запрещен")

    # Получаем информацию о группе
    group_name = "Не назначена"
    if user.get('group_id'):
        group = user_manager.get_group(user['group_id'])
        if group:
            group_name = group['name']

    # Получаем статистику
    grades_manager = GradesManager()
    attendance_manager = AttendanceManager()

    average_grade = grades_manager.get_average_grade(user['id'])
    attendance_stats = attendance_manager.get_student_attendance_stats(user['id'], user.get('group_id'))

    profile_text = (
        f"👤 Ваш профиль:\n\n"
        f"🎒 ФИО: {user['full_name']}\n"
        f"📞 Телефон: {user['phone']}\n"
        f"🏫 Группа: {group_name}\n"
        f"📅 Дата регистрации: {user['created_at']}\n\n"

        f"📊 Статистика:\n"
        f"⭐ Средний балл: {average_grade:.1f}\n"
        f"📈 Посещаемость: {attendance_stats.get('attendance_rate', 0)}%\n"
        f"🎯 Статус: {user['status']}"
    )
    await message.answer(profile_text)


@router.message(F.text == "📝 Мои задания")
async def student_assignments(message: Message):
    """Показывает задания ученика с реальными данными"""
    user_manager = UserManager()
    user = user_manager.get_user(message.from_user.id)

    if not user or user['role'] != 'student' or user['status'] != 'active':
        return await message.answer("❌ Доступ запрещен")

    # Проверяем, есть ли у ученика группа
    if not user.get('group_id'):
        await message.answer(
            "📭 У вас нет назначенной группы.\n\n"
            "Обратитесь к администратору для назначения в группу."
        )
        return

    assignment_manager = AssignmentManager()
    assignments = assignment_manager.get_assignments_for_student(user['id'])

    if not assignments:
        await message.answer(
            "📭 У вас пока нет заданий\n\n"
            "Задания появятся здесь, когда учитель их создаст."
        )
        return

    assignments_text = "📚 Ваши задания:\n\n"

    for i, assignment in enumerate(assignments, 1):
        assignments_text += f"{i}. 🔹 **{assignment['title']}**\n"

        if assignment.get('description'):
            assignments_text += f"   📝 {assignment['description']}\n"

        if assignment.get('deadline'):
            # Форматируем дату
            deadline = assignment['deadline']
            if isinstance(deadline, str):
                assignments_text += f"   ⏰ До: {deadline}\n"
            else:
                assignments_text += f"   ⏰ До: {deadline.strftime('%d.%m.%Y')}\n"

        if assignment.get('teacher_name'):
            assignments_text += f"   👨‍🏫 Преподаватель: {assignment['teacher_name']}\n"

        assignments_text += "\n"

    assignments_text += f"📊 Всего заданий: {len(assignments)}"

    await message.answer(assignments_text)