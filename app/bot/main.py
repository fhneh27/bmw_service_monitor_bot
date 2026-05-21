import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.bot.handlers import register_handlers


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    token = os.getenv("TG_BOT_TOKEN")
    if not token:
        raise RuntimeError("TG_BOT_TOKEN is not set")

    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    me = await bot.get_me()
    logging.info("Bot started: @%s (%s)", me.username, me.id)

    await bot.delete_webhook(drop_pending_updates=True)

    dp = Dispatcher()
    register_handlers(dp)

    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
