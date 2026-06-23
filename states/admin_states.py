# FSM states for tracking what input the admin is currently expected to provide
from aiogram.fsm.state import State, StatesGroup


class AdminAction(StatesGroup):
    writing_approve_comment = State()  # admin is typing a comment to attach to an approval
    writing_reject_reason = State()    # admin is typing the reason for rejection
    writing_to_user = State()          # admin is composing a free message to the user
