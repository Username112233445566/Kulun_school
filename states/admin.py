from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    creating_group = State()
    creating_group_for_user = State()
    editing_group_name = State()
    assigning_teacher = State()
    adding_students = State()