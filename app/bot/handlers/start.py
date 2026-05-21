from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.bot.keyboards import build_main_menu_keyboard
from app.bot.presentation import format_start_message, send_optional_sticker
from app.services.user_service import get_or_create_user

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    tg_user = message.from_user
    if tg_user is None:
        await message.answer("Не вдалося визначити користувача.")
        return

    get_or_create_user(
        telegram_id=tg_user.id,
        username=tg_user.username,
        first_name=tg_user.first_name,
        last_name=tg_user.last_name,
    )
    await send_optional_sticker(message, "start")

    await message.answer(
        format_start_message(tg_user.first_name),
        reply_markup=build_main_menu_keyboard(),
    )
