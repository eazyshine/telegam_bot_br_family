from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def submission_kb(section: str, sub_id: int) -> InlineKeyboardMarkup:
    # "misc" section has no accept/reject — admins can only reply directly to the user
    builder = InlineKeyboardBuilder()

    if section != "misc":
        builder.button(text="✅ Принять", callback_data=f"accept_{sub_id}")
        builder.button(text="❌ Отклонить", callback_data=f"reject_{sub_id}")
        builder.button(text="✉️ Написать", callback_data=f"write_{sub_id}")
        builder.adjust(2, 1)  # first row: 2 buttons, second row: 1 button
    else:
        builder.button(text="✉️ Написать пользователю", callback_data=f"write_{sub_id}")
        builder.adjust(1)

    return builder.as_markup()
