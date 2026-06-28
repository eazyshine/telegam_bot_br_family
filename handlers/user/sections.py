from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.user_kb import back_kb
from states.user_states import UserSection

router = Router()

# Section instruction texts shown to the user after selecting a category
COMPLAINT_TEXT = (
    "Примечание: Жалоба на игрока принимается только в том случае, если есть неоспоримые "
    "доказательства, что игрок использует стороннее ПО, сборка, читы и также в жалобе "
    "принимаются только видеодоказательства с /time.\n\n"
    "1. Ваш никнейм:\n"
    "2. Никнейм игрока:\n"
    "3. Причина подачи жалобы:\n"
    "4. Доказательства(прикрепите к заявке, отправив медиа в боте):"
)

DEPUTY_TEXT = (
    "Заявка на заместителя:\n\n"
    "1. Ваш юзернейм в телеграм\n"
    "2. Ваш игровой никнейм\n"
    "3. Ваш опыт в других семьях на посту заместителя\n"
    "4. Ваш игровой онлайн\n"
    "5. Ваш возраст\n"
    "6. Сколько вы находитесь в нашей семье\n"
    "7. Оценка вашей стрельбы от 1/10"
)

SENIOR_TEXT = (
    "Заявка на старший состав:\n\n"
    "1. Ваш юзернейм в телеграм\n"
    "2. Ваш игровой никнейм\n"
    "3. Ваш игровой онлайн\n"
    "4. Ваш возраст\n"
    "5. Сколько вы находитесь в семье (не меньше полугода)\n"
    "6. Оценка вашей стрельбы от 1/10\n"
    "7. Оценка вашей адекватности от 1/10\n"
    "8. В каких семьях вы находились до нашей семьи"
)

MISC_TEXT = "Опишите ситуацию или задайте вопрос, администрация как можно скорее ответит на него."


@router.message(F.text == "Жалоба на игроков нашей семьи")
async def section_complaint(message: Message, state: FSMContext):
    await state.set_state(UserSection.complaint)
    await message.answer(COMPLAINT_TEXT, reply_markup=back_kb())


@router.message(F.text == "Заявка на заместителя")
async def section_deputy(message: Message, state: FSMContext):
    await state.set_state(UserSection.deputy)
    await message.answer(DEPUTY_TEXT, reply_markup=back_kb())


@router.message(F.text == "Заявка на Старший Состав")
async def section_senior(message: Message, state: FSMContext):
    await state.set_state(UserSection.senior)
    await message.answer(SENIOR_TEXT, reply_markup=back_kb())


@router.message(F.text == "Прочее")
async def section_misc(message: Message, state: FSMContext):
    await state.set_state(UserSection.misc)
    await message.answer(MISC_TEXT, reply_markup=back_kb())
