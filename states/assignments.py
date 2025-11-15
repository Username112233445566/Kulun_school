from aiogram.fsm.state import State, StatesGroup

class AssignmentStates(StatesGroup):
    choosing_group = State()
    entering_title = State()
    entering_description = State()
    setting_deadline = State()