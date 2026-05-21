import os
from html import escape

from aiogram.types import Message

SOURCE_LABELS = {
    "bmw-official": "BMW Official",
    "service-partner": "Certified Partner",
    "independent-garage": "Independent Garage",
}


def format_start_message(first_name: str | None) -> str:
    name = escape(first_name or "друже")
    return (
        "<b>BMW Service Monitor</b>\n"
        f"Вітаю, <b>{name}</b>.\n\n"
        "Я допоможу швидко переглянути ціни на послуги BMW, "
        "зберегти потрібні позиції в обране та повернутися до них в один тап."
    )


def format_profile_message(user, favorites_count: int) -> str:
    display_name = " ".join(part for part in [user.first_name, user.last_name] if part) or "Користувач BMW"
    username = f"@{escape(user.username)}" if user.username else "не вказано"
    return (
        "<b>👤 Профіль</b>\n"
        f"Ім'я: <b>{escape(display_name)}</b>\n"
        f"Username: <code>{username}</code>\n"
        f"В обраному: <b>{favorites_count}</b>\n"
        "Статус: <b>активний</b>"
    )


def format_model_prompt() -> str:
    return (
        "<b>📊 Каталог цін</b>\n"
        "Введи модель BMW у довільному форматі.\n"
        "Наприклад: <code>X5 G05</code>"
    )


def format_model_selected_message(car_model: str) -> str:
    return (
        "<b>Модель обрано</b>\n"
        f"Поточна модель: <code>{escape(car_model)}</code>\n\n"
        "Тепер обери потрібну послугу."
    )


def format_prices_message(service_name: str, car_model: str, prices, is_favorite: bool) -> str:
    best_price = prices[0].price
    max_price = prices[-1].price
    spread = f"{best_price} EUR" if best_price == max_price else f"{best_price}-{max_price} EUR"
    favorite_status = "⭐ в обраному" if is_favorite else "· не збережено"

    lines = [
        f"<b>{escape(service_name)}</b>",
        f"Авто: <code>{escape(car_model)}</code>",
        "",
        f"Найкраща ціна: <b>{best_price} EUR</b>",
        f"Діапазон: <b>{spread}</b>",
        f"Статус: <b>{favorite_status}</b>",
        "",
        "<b>Пропозиції</b>",
    ]
    for index, item in enumerate(prices, start=1):
        source = SOURCE_LABELS.get(item.source, item.source or "Unknown source")
        lines.append(f"{index}. {escape(source)} - <b>{item.price} EUR</b>")

    return "\n".join(lines)


def format_favorites_summary(favorites) -> str:
    return (
        "<b>⭐ Обране</b>\n"
        f"Збережено позицій: <b>{len(favorites)}</b>\n\n"
        "Натисни на зв'язку, щоб одразу відкрити актуальні ціни, "
        "або видали зайве прямо з цього екрана."
    )


async def send_optional_sticker(message: Message, sticker_key: str) -> None:
    sticker_id = os.getenv(f"STICKER_{sticker_key.upper()}")
    if not sticker_id:
        return

    try:
        await message.answer_sticker(sticker_id)
    except Exception:
        return
