from aiogram.fsm.state import State, StatesGroup

class AttendanceStates(StatesGroup):
    choosing_group = State()
    choosing_date = State()
    marking_attendance = State()