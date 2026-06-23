from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from config import ADMIN_IDS
from database.db import db
from states.admin_states import AdminAction
from utils.formatters import approval_msg

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.callback_query(lambda c: c.data and c.data.startswith("accept_"))
async def cb_accept(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа.", show_alert=True)
        return

    sub_id = int(callback.data.split("_", 1)[1])
    sub = await db.get_submission(sub_id)

    if not sub:
        await callback.answer("Заявка не найдена.", show_alert=True)
        return

    # Prevent the second admin from processing an already-handled submission
    if sub["status"] != "pending":
        await callback.answer("Эта заявка уже обработана.", show_alert=True)
        return

    if sub["section"] == "complaint":
        # Complaints require a mandatory admin comment sent to the user upon approval
        await state.set_state(AdminAction.writing_approve_comment)
        await state.update_data(sub_id=sub_id, user_id=sub["user_id"])
        await callback.message.answer("Введите комментарий к жалобе (он будет отправлен пользователю):")
        await callback.answer()
        return

    await db.update_status(sub_id, "approved", callback.from_user.id)

    try:
        await bot.send_message(sub["user_id"], approval_msg(sub["section"]))
    except Exception:
        pass

    await callback.message.answer(f"✅ Заявка #{sub_id} одобрена. Пользователь уведомлён.")
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("reject_"))
async def cb_reject(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа.", show_alert=True)
        return

    sub_id = int(callback.data.split("_", 1)[1])
    sub = await db.get_submission(sub_id)

    if not sub:
        await callback.answer("Заявка не найдена.", show_alert=True)
        return

    if sub["status"] != "pending":
        await callback.answer("Эта заявка уже обработана.", show_alert=True)
        return

    # Ask admin to type the rejection reason before updating the DB
    await state.set_state(AdminAction.writing_reject_reason)
    await state.update_data(sub_id=sub_id, user_id=sub["user_id"], section=sub["section"])
    await callback.message.answer("Введите причину отклонения:")
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("write_"))
async def cb_write(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа.", show_alert=True)
        return

    sub_id = int(callback.data.split("_", 1)[1])
    sub = await db.get_submission(sub_id)

    if not sub:
        await callback.answer("Заявка не найдена.", show_alert=True)
        return

    # Writing to user does not change the submission status
    await state.set_state(AdminAction.writing_to_user)
    await state.update_data(sub_id=sub_id, user_id=sub["user_id"])
    await callback.message.answer("Введите сообщение для пользователя:")
    await callback.answer()
