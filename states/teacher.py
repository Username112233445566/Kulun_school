from aiogram.fsm.state import State, StatesGroup

class TeacherStates(StatesGroup):
    choosing_group_for_attendance = State()
    marking_attendance = State()
    choosing_group_for_assignment = State()
    creating_assignment_title = State()
    creating_assignment_description = State()
    creating_assignment_deadline = State()
    choosing_group_for_grades = State()
    choosing_subject_for_grades = State()
    setting_grades = State()
    viewing_group_performance = State()
