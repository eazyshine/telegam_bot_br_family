from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def main_menu_kb() -> ReplyKeyboardMarkup:
    """
    Build the main menu ReplyKeyboard shown after /start.

    Buttons are arranged in a 2×2 grid.
    The keyboard disappears after the user taps a button (one_time_keyboard).

    Returns:
        ReplyKeyboardMarkup with the four main section buttons.
    """
    # one_time_keyboard hides the keyboard after the user taps a button
    builder = ReplyKeyboardBuilder()
    builder.button(text="Жалоба на игроков нашей семьи")
    builder.button(text="Заявка на заместителя")
    builder.button(text="Заявка на Старший Состав")
    builder.button(text="Прочее")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def back_kb() -> InlineKeyboardMarkup:
    """
    Build the inline keyboard with a single 'Назад' button.

    Attached to every section form so the user can return to the main menu.
    The form message is deleted when the button is pressed.

    Returns:
        InlineKeyboardMarkup with the back button.
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙Назад", callback_data="back_to_main")
    return builder.as_markup()
