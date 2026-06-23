from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import ADMIN_IDS
from database.db import db
from keyboards.admin_kb import submission_kb
from states.user_states import UserSection
from utils.formatters import confirm_msg, format_admin_msg

router = Router()


async def _handle_submission(message: Message, state: FSMContext, bot: Bot, section: str):
    user_id = message.from_user.id
    username = message.from_user.username
    # Fall back to caption (for media messages) or a placeholder if the message has no text
    content = message.text or message.caption or "[медиа без текста]"

    sub_id = await db.add_submission(user_id, username, section, content)

    await message.answer(confirm_msg(section))

    # Forward the submission to both admins; silently skip if admin has blocked the bot
    admin_text = format_admin_msg(user_id, username, section, content)
    kb = submission_kb(section, sub_id)

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            pass

    await state.clear()


@router.message(UserSection.complaint)
async def receive_complaint(message: Message, state: FSMContext, bot: Bot):
    await _handle_submission(message, state, bot, "complaint")


@router.message(UserSection.deputy)
async def receive_deputy(message: Message, state: FSMContext, bot: Bot):
    await _handle_submission(message, state, bot, "deputy")


@router.message(UserSection.senior)
async def receive_senior(message: Message, state: FSMContext, bot: Bot):
    await _handle_submission(message, state, bot, "senior")


@router.message(UserSection.misc)
async def receive_misc(message: Message, state: FSMContext, bot: Bot):
    await _handle_submission(message, state, bot, "misc")
