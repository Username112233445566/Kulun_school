from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    choosing_role = State()
    entering_name = State()
    entering_phone = State()