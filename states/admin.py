from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    creating_group = State()
    creating_group_for_user = State()
    editing_group_name = State()
    assigning_teacher = State()
    adding_students = State()
    adding_subject_name = State()
    adding_subject_description = State()
    managing_schedule = State()
    adding_schedule_day = State()
    adding_schedule_time = State()
    adding_schedule_subject = State()