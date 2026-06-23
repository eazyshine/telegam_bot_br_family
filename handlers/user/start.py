from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards.user_kb import main_menu_kb

router = Router()

WELCOME_TEXT = (
    "Здравствуйте, данный бот семьи Yakudza Youngboyzz. "
    "Выберите раздел по которому хотите обратиться."
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    # Clear any leftover FSM state so the user always starts fresh
    await state.clear()
    await message.answer(WELCOME_TEXT, reply_markup=main_menu_kb())


@router.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()  # remove the section form before sending the main menu
    await callback.message.answer(WELCOME_TEXT, reply_markup=main_menu_kb())
    await callback.answer()
