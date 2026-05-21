from aiogram import Dispatcher

from .prices import router as prices_router
from .favorites import router as favorites_router
from .profile import router as profile_router
from .start import router as start_router


def register_handlers(dp: Dispatcher) -> None:
    dp.include_router(start_router)
    dp.include_router(profile_router)
    dp.include_router(favorites_router)
    dp.include_router(prices_router)
