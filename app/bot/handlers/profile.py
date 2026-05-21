from aiogram import F, Router
from aiogram.types import Message

from app.bot.presentation import format_profile_message
from app.services.favorite_service import get_favorites_count
from app.services.user_service import get_user_by_telegram_id

router = Router()


@router.message(F.text == "👤 Профіль")
async def show_profile(message: Message) -> None:
    tg_user = message.from_user
    if tg_user is None:
        await message.answer("Не вдалося визначити користувача.")
        return

    user = get_user_by_telegram_id(tg_user.id)
    if not user:
        await message.answer("Тебе поки немає в базі. Натисни /start")
        return

    favorites_count = get_favorites_count(user.id)
    await message.answer(format_profile_message(user, favorites_count))
