__all__ = ("VerifyUserCallback",)

from aiogram.filters.callback_data import CallbackData


class VerifyUserCallback(CallbackData, prefix="verify_user"):
    action: str = "confirm"
    user_id: int
