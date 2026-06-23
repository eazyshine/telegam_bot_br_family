# FSM states for tracking which section the user is currently filling out
from aiogram.fsm.state import State, StatesGroup


class UserSection(StatesGroup):
    complaint = State()  # complaint about a family member
    deputy = State()     # application for deputy position
    senior = State()     # application for senior staff position
    misc = State()       # general question or message
