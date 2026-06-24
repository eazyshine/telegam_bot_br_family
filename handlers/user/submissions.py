from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import ADMIN_IDS
from database.db import db
from keyboards.admin_kb import submission_kb
from states.user_states import UserSection
from utils.formatters import confirm_msg, format_admin_msg

router = Router()

# Human-readable labels for each media type stored in the database
MEDIA_LABELS = {
    "photo": "[фото]",
    "video": "[видео]",
    "document": "[документ]",
    "audio": "[аудио]",
    "voice": "[голосовое сообщение]",
    "video_note": "[видео-кружок]",
    "sticker": "[стикер]",
    "animation": "[гифка]",
}


def get_content(message: Message) -> str:
    """
    Extract human-readable content from any message type.

    For text messages returns the text.
    For media with a caption returns the caption.
    For media without a caption returns a label like '[фото]', '[видео]', etc.

    Args:
        message: Incoming Telegram message.

    Returns:
        A string representing the message content for storage and display.
    """
    if message.text:
        return message.text

    caption = message.caption or ""

    for attr, label in MEDIA_LABELS.items():
        if getattr(message, attr):
            return f"{label} {caption}".strip()

    return caption or "[медиа]"


async def _handle_submission(message: Message, state: FSMContext, bot: Bot, section: str):
    """
    Core handler called by every section-specific handler.

    Steps:
        1. Save the submission to the database.
        2. Send a section-specific confirmation back to the user.
        3. Forward the formatted header to all admins with action buttons.
        4. Copy the original message to admins so they see the actual media.
        5. Clear the user's FSM state.

    Args:
        message: Incoming Telegram message from the user.
        state:   FSM context used to clear the active state after saving.
        bot:     Bot instance needed to push messages to admin IDs.
        section: Section key identifying which form was submitted.
    """
    user_id = message.from_user.id
    username = message.from_user.username
    content = get_content(message)

    sub_id = await db.add_submission(user_id, username, section, content)

    await message.answer(confirm_msg(section))

    # Send the formatted header with action buttons first, then copy the original
    # message so admins see the actual media (photo, video, document, etc.)
    admin_text = format_admin_msg(user_id, username, section, content)
    kb = submission_kb(section, sub_id)

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_text, reply_markup=kb, parse_mode="HTML")
            # Copy the original message only if it contains media
            if not message.text:
                await bot.copy_message(
                    chat_id=admin_id,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id,
                )
        except Exception:
            pass

    await state.clear()


@router.message(UserSection.complaint)
async def receive_complaint(message: Message, state: FSMContext, bot: Bot):
    """Handle a message submitted while in the complaint section."""
    await _handle_submission(message, state, bot, "complaint")


@router.message(UserSection.deputy)
async def receive_deputy(message: Message, state: FSMContext, bot: Bot):
    """Handle a message submitted while in the deputy application section."""
    await _handle_submission(message, state, bot, "deputy")


@router.message(UserSection.senior)
async def receive_senior(message: Message, state: FSMContext, bot: Bot):
    """Handle a message submitted while in the senior staff application section."""
    await _handle_submission(message, state, bot, "senior")


@router.message(UserSection.misc)
async def receive_misc(message: Message, state: FSMContext, bot: Bot):
    """Handle a message submitted while in the misc (general) section."""
    await _handle_submission(message, state, bot, "misc")
