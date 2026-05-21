from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards import build_price_result_keyboard, build_services_keyboard
from app.bot.presentation import (
    format_model_prompt,
    format_model_selected_message,
    format_prices_message,
    send_optional_sticker,
)
from app.services.favorite_service import (
    add_favorite,
    get_favorite_by_triplet,
    remove_favorite_by_triplet,
)
from app.services.price_service import (
    ensure_default_services,
    ensure_stub_prices,
    get_service_by_id,
    get_services,
)
from app.services.user_service import get_user_by_telegram_id

router = Router()


class PriceFlow(StatesGroup):
    waiting_for_car_model = State()
    waiting_for_service = State()


@router.message(F.text == "📊 Каталог цін")
async def start_price_flow(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(PriceFlow.waiting_for_car_model)
    await send_optional_sticker(message, "price")
    await message.answer(format_model_prompt())


@router.message(PriceFlow.waiting_for_car_model)
async def get_car_model(message: Message, state: FSMContext) -> None:
    car_model = (message.text or "").strip()
    if not car_model:
        await message.answer(
            "Не зміг розпізнати модель.\n"
            "Спробуй у форматі на кшталт <code>X5 G05</code>."
        )
        return

    ensure_default_services()
    services = get_services()
    await state.update_data(car_model=car_model)
    await state.set_state(PriceFlow.waiting_for_service)
    await message.answer(
        format_model_selected_message(car_model),
        reply_markup=build_services_keyboard(services),
    )


async def _render_prices(callback: CallbackQuery, state: FSMContext, service_id: int) -> None:
    data = await state.get_data()
    car_model = data.get("car_model")
    if not car_model:
        await callback.answer("Спочатку відкрий каталог цін", show_alert=True)
        return

    service = get_service_by_id(service_id)
    if not service:
        await callback.answer("Послугу не знайдено", show_alert=True)
        return

    user = get_user_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer("Спочатку натисни /start", show_alert=True)
        return

    prices = ensure_stub_prices(service_id=service_id, car_model=car_model)
    services = get_services()
    favorite = get_favorite_by_triplet(
        user_id=user.id,
        service_id=service_id,
        car_model=car_model,
    )
    await callback.message.edit_text(
        format_prices_message(
            service_name=service.name,
            car_model=car_model,
            prices=prices,
            is_favorite=favorite is not None,
        ),
        reply_markup=build_price_result_keyboard(
            services=services,
            selected_service_id=service_id,
            is_favorite=favorite is not None,
        ),
    )


@router.callback_query(F.data.startswith("service:"))
async def select_service(callback: CallbackQuery, state: FSMContext) -> None:
    service_id = int(callback.data.split(":", 1)[1])
    await _render_prices(callback, state, service_id)
    await callback.answer()


@router.callback_query(F.data == "prices_restart")
async def restart_price_flow(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(PriceFlow.waiting_for_car_model)
    await callback.message.edit_text(format_model_prompt())
    await callback.answer("Можна ввести нову модель")


@router.callback_query(F.data.startswith("favorite_add:"))
async def save_favorite(callback: CallbackQuery, state: FSMContext) -> None:
    user = get_user_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer("Спочатку натисни /start", show_alert=True)
        return

    data = await state.get_data()
    car_model = data.get("car_model")
    if not car_model:
        await callback.answer("Спочатку обери модель у каталозі цін", show_alert=True)
        return

    service_id = int(callback.data.split(":", 1)[1])
    _, created = add_favorite(
        user_id=user.id,
        service_id=service_id,
        car_model=car_model,
    )
    await _render_prices(callback, state, service_id)
    if created:
        await callback.answer("Позицію додано в обране")
        return

    await callback.answer("Вже є в обраному", show_alert=True)


@router.callback_query(F.data.startswith("favorite_remove_current:"))
async def remove_current_favorite(callback: CallbackQuery, state: FSMContext) -> None:
    user = get_user_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer("Спочатку натисни /start", show_alert=True)
        return

    data = await state.get_data()
    car_model = data.get("car_model")
    if not car_model:
        await callback.answer("Спочатку обери модель у каталозі цін", show_alert=True)
        return

    service_id = int(callback.data.split(":", 1)[1])
    removed = remove_favorite_by_triplet(
        user_id=user.id,
        service_id=service_id,
        car_model=car_model,
    )
    await _render_prices(callback, state, service_id)
    if removed:
        await callback.answer("Позицію прибрано з обраного")
        return

    await callback.answer("В обраному вже порожньо", show_alert=True)
