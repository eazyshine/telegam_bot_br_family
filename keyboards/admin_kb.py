from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def submission_kb(section: str, sub_id: int) -> InlineKeyboardMarkup:
    """
    Build the admin action keyboard attached to every incoming submission.

    Layout varies by section:
    - complaint / deputy / senior: ✅ Принять | ❌ Отклонить (row 1)
                                   ✉️ Написать              (row 2)
    - misc: ✉️ Написать пользователю only — no accept/reject needed.

    Callback data format: '<action>_<sub_id>' (e.g. 'accept_42').

    Args:
        section: Section key to determine which buttons to show.
        sub_id:  Submission ID embedded in the callback data.

    Returns:
        InlineKeyboardMarkup with the appropriate action buttons.
    """
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


def back_to_sub_kb(sub_id: int) -> InlineKeyboardMarkup:
    """
    Build the '🔙 Назад' inline keyboard attached to every admin input prompt
    (approve comment, reject reason, write to user).

    Pressing the button clears the admin's FSM state and re-shows the original
    submission with its action buttons.

    Args:
        sub_id: Submission ID embedded in the callback data.

    Returns:
        InlineKeyboardMarkup with the back button.
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад", callback_data=f"back_to_sub_{sub_id}")
    return builder.as_markup()
