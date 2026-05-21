from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.handlers.prices import PriceFlow
from app.bot.keyboards import build_favorites_keyboard, build_price_result_keyboard
from app.bot.presentation import format_favorites_summary, format_prices_message, send_optional_sticker
from app.services.favorite_service import (
    clear_favorites_for_user,
    get_favorite_by_triplet,
    get_favorite_for_user,
    get_favorites_for_user,
    remove_favorite,
)
from app.services.price_service import ensure_stub_prices, get_services
from app.services.user_service import get_user_by_telegram_id

router = Router()


@router.message(F.text == "⭐ Обране")
async def show_favorites(message: Message) -> None:
    tg_user = message.from_user
    if tg_user is None:
        await message.answer("Не вдалося визначити користувача.")
        return

    user = get_user_by_telegram_id(tg_user.id)
    if not user:
        await message.answer("Тебе поки немає в базі. Натисни /start")
        return

    favorites = get_favorites_for_user(user.id)
    if not favorites:
        await message.answer("Обране поки порожнє.")
        return

    await send_optional_sticker(message, "favorite")
    await message.answer(
        format_favorites_summary(favorites),
        reply_markup=build_favorites_keyboard(favorites),
    )


@router.callback_query(F.data.startswith("favorite_open:"))
async def open_favorite(callback: CallbackQuery, state: FSMContext) -> None:
    user = get_user_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer("Спочатку натисни /start", show_alert=True)
        return

    favorite_id = int(callback.data.split(":", 1)[1])
    favorite = get_favorite_for_user(favorite_id=favorite_id, user_id=user.id)
    if not favorite:
        await callback.answer("Позицію не знайдено", show_alert=True)
        return

    await state.update_data(car_model=favorite.car_model)
    await state.set_state(PriceFlow.waiting_for_service)

    prices = ensure_stub_prices(
        service_id=favorite.service_id,
        car_model=favorite.car_model,
    )
    services = get_services()
    existing = get_favorite_by_triplet(
        user_id=user.id,
        service_id=favorite.service_id,
        car_model=favorite.car_model,
    )
    await callback.message.edit_text(
        format_prices_message(
            service_name=favorite.service.name,
            car_model=favorite.car_model,
            prices=prices,
            is_favorite=existing is not None,
        ),
        reply_markup=build_price_result_keyboard(
            services=services,
            selected_service_id=favorite.service_id,
            is_favorite=existing is not None,
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("favorite_remove:"))
async def remove_favorite_entry(callback: CallbackQuery) -> None:
    user = get_user_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer("Спочатку натисни /start", show_alert=True)
        return

    favorite_id = int(callback.data.split(":", 1)[1])
    removed = remove_favorite(favorite_id=favorite_id, user_id=user.id)
    favorites = get_favorites_for_user(user.id)

    if not favorites:
        await callback.message.edit_text("<b>⭐ Обране</b>\nСписок тепер порожній.")
        if removed:
            await callback.answer("Позицію видалено")
            return

        await callback.answer("Позицію вже було видалено", show_alert=True)
        return

    await callback.message.edit_text(
        format_favorites_summary(favorites),
        reply_markup=build_favorites_keyboard(favorites),
    )
    if removed:
        await callback.answer("Позицію видалено")
        return

    await callback.answer("Позицію вже було видалено", show_alert=True)


@router.callback_query(F.data == "favorite_clear_all")
async def clear_favorites(callback: CallbackQuery) -> None:
    user = get_user_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer("Спочатку натисни /start", show_alert=True)
        return

    removed_count = clear_favorites_for_user(user.id)
    await callback.message.edit_text("<b>⭐ Обране</b>\nСписок очищено.")
    if removed_count:
        await callback.answer("Обране очищено")
        return

    await callback.answer("Очищати не було чого", show_alert=True)
