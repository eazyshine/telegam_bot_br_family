import asyncio
import logging

from aiogram.types import BotCommand

from loader import bot, dp
from router import register_routers
from database.db import db


async def set_commands():
    # Register visible bot commands in the Telegram menu (the "/" button)
    await bot.set_my_commands([
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="declined", description="Список отклонённых заявок"),
        BotCommand(command="approved", description="Список одобренных заявок"),
    ])


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    await db.create_pool()
    await db.init_tables()  # creates submissions table if it doesn't exist
    register_routers()
    await set_commands()

    try:
        await dp.start_polling(bot)
    finally:
        await db.close()  # gracefully close the connection pool on shutdown


if __name__ == "__main__":
    asyncio.run(main())
