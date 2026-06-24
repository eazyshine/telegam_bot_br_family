from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import ADMIN_IDS
from database.db import db
from utils.formatters import format_submission_detail

router = Router()

# Telegram hard limit is 4096 chars; stay under it to avoid split errors
MAX_MESSAGE_LENGTH = 4000


def is_admin(user_id: int) -> bool:
    """Return True if the given Telegram user ID belongs to an admin."""
    return user_id in ADMIN_IDS


async def send_list(message: Message, status: str, header: str):
    """
    Fetch all submissions with the given status and send them to the admin.

    Long lists are split into multiple messages to stay within Telegram's
    4096-character message limit. Silently ignores non-admin callers.

    Args:
        message: Admin's command message used to reply.
        status:  Database status to filter by ('approved' or 'rejected').
        header:  Title line shown before the list (e.g. '✅ Одобренные заявки').
    """
    if not is_admin(message.from_user.id):
        return

    submissions = await db.list_by_status(status)

    if not submissions:
        await message.answer(f"{header}\n\nНет записей.")
        return

    await message.answer(f"{header} — {len(submissions)} шт.\n")

    # Send in chunks to avoid hitting the Telegram message length limit
    chunk = ""
    for sub in submissions:
        block = format_submission_detail(sub) + "\n"
        if len(chunk) + len(block) > MAX_MESSAGE_LENGTH:
            await message.answer(chunk, parse_mode="HTML")
            chunk = ""
        chunk += block

    if chunk:
        await message.answer(chunk, parse_mode="HTML")


@router.message(Command("declined"))
async def cmd_declined(message: Message):
    """Show all rejected submissions. Admin-only."""
    await send_list(message, "rejected", "❌ Отклонённые заявки")


@router.message(Command("approved"))
async def cmd_approved(message: Message):
    """Show all approved submissions. Admin-only."""
    await send_list(message, "approved", "✅ Одобренные заявки")
