from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def build_main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Каталог цін"), KeyboardButton(text="⭐ Обране")],
            [KeyboardButton(text="👤 Профіль")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Обери дію",
    )


def build_services_keyboard(services) -> InlineKeyboardMarkup:
    rows = []
    current_row = []
    for service in services:
        current_row.append(
            InlineKeyboardButton(text=service.name, callback_data=f"service:{service.id}")
        )
        if len(current_row) == 2:
            rows.append(current_row)
            current_row = []

    if current_row:
        rows.append(current_row)

    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_price_result_keyboard(services, selected_service_id: int, is_favorite: bool) -> InlineKeyboardMarkup:
    rows = []
    current_row = []
    for service in services:
        label = service.name
        if service.id == selected_service_id:
            label = f"✅ {service.name}"

        current_row.append(
            InlineKeyboardButton(text=label, callback_data=f"service:{service.id}")
        )
        if len(current_row) == 2:
            rows.append(current_row)
            current_row = []

    if current_row:
        rows.append(current_row)

    action_text = "🗑 Прибрати з обраного" if is_favorite else "⭐ Додати в обране"
    action_callback = (
        f"favorite_remove_current:{selected_service_id}"
        if is_favorite
        else f"favorite_add:{selected_service_id}"
    )
    rows.append([InlineKeyboardButton(text=action_text, callback_data=action_callback)])
    rows.append([InlineKeyboardButton(text="↺ Змінити модель", callback_data="prices_restart")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_favorites_keyboard(favorites) -> InlineKeyboardMarkup:
    rows = []
    for favorite in favorites:
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"⭐ {favorite.service.name} | {favorite.car_model}",
                    callback_data=f"favorite_open:{favorite.id}",
                ),
                InlineKeyboardButton(
                    text="🗑",
                    callback_data=f"favorite_remove:{favorite.id}",
                ),
            ]
        )

    rows.append([InlineKeyboardButton(text="🧹 Очистити все обране", callback_data="favorite_clear_all")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
