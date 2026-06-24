from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.db import db
from states.admin_states import AdminAction
from utils.formatters import approval_msg, rejection_msg

router = Router()


@router.message(AdminAction.writing_approve_comment)
async def receive_approve_comment(message: Message, state: FSMContext, bot: Bot):
    """
    Receive the admin's approval comment for a complaint.

    Triggered after the admin pressed ✅ Принять on a complaint submission
    and was prompted to type a comment. Saves the decision and notifies the user.
    """
    data = await state.get_data()
    sub_id = data["sub_id"]
    user_id = data["user_id"]
    comment = message.text

    await db.update_status(sub_id, "approved", message.from_user.id, comment, message.from_user.username)

    try:
        await bot.send_message(user_id, approval_msg("complaint", comment))
    except Exception:
        pass

    await state.clear()
    await message.answer(f"✅ Жалоба #{sub_id} одобрена. Комментарий отправлен пользователю.")


@router.message(AdminAction.writing_reject_reason)
async def receive_reject_reason(message: Message, state: FSMContext, bot: Bot):
    """
    Receive the admin's rejection reason for any section.

    Triggered after the admin pressed ❌ Отклонить and was prompted to type
    a reason. Saves the decision and sends a section-appropriate rejection
    message to the user.
    """
    data = await state.get_data()
    sub_id = data["sub_id"]
    user_id = data["user_id"]
    section = data["section"]
    reason = message.text

    await db.update_status(sub_id, "rejected", message.from_user.id, reason, message.from_user.username)

    try:
        await bot.send_message(user_id, rejection_msg(section, reason))
    except Exception:
        pass

    await state.clear()
    await message.answer(f"❌ Заявка #{sub_id} отклонена. Пользователь уведомлён.")


@router.message(AdminAction.writing_to_user)
async def receive_msg_to_user(message: Message, state: FSMContext, bot: Bot):
    """
    Forward a free-form admin message to the original submitter.

    Triggered after the admin pressed ✉️ Написать. The submission status
    is not changed — this is purely a communication channel.
    """
    data = await state.get_data()
    user_id = data["user_id"]
    sub_id = data["sub_id"]
    text = message.text

    try:
        await bot.send_message(user_id, f"Сообщение от администрации:\n\n{text}")
        await message.answer(f"✉️ Сообщение пользователю по заявке #{sub_id} отправлено.")
    except Exception:
        # User may have blocked the bot
        await message.answer("Не удалось отправить сообщение пользователю.")

    await state.clear()
