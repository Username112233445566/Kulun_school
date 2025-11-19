from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict
from services.subjects_manager import SubjectsManager

def get_teacher_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мои группы"), KeyboardButton(text="Посещаемость")],
            [KeyboardButton(text="Создать задание"), KeyboardButton(text="Выставить оценки")],
            [KeyboardButton(text="Успеваемость")]
        ],
        resize_keyboard=True
    )

def get_groups_keyboard(groups: List[Dict]):
    keyboard = []
    for group in groups:
        keyboard.append([KeyboardButton(text=group['name'])])
    keyboard.append([KeyboardButton(text="Назад")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_attendance_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Присутствовал"), KeyboardButton(text="Отсутствовал")],
            [KeyboardButton(text="Опоздал"), KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )

def get_subjects_keyboard():
    subjects_manager = SubjectsManager()
    subjects = subjects_manager.get_all_subjects()

    keyboard = []

    if not subjects:
        keyboard.append([KeyboardButton(text="Нет доступных предметов")])
    else:
        row = []
        for i, subject in enumerate(subjects):
            row.append(KeyboardButton(text=subject['name']))
            if len(row) == 2 or i == len(subjects) - 1:
                keyboard.append(row)
                row = []

    keyboard.append([KeyboardButton(text="Назад")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_grades_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="5"), KeyboardButton(text="4"), KeyboardButton(text="3")],
            [KeyboardButton(text="2"), KeyboardButton(text="1")],
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )

def get_confirmation_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Подтвердить"), KeyboardButton(text="Отменить")]
        ],
        resize_keyboard=True
    )