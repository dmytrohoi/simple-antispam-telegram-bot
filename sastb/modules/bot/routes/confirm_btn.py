__all__ = ("router",)

from datetime import timedelta, datetime
from typing import TYPE_CHECKING

from loguru import logger

from aiogram import F, Router
from aiogram.types import InaccessibleMessage, ChatPermissions

from sastb.config.config import ApplicationSettings
from sastb.modules.scheduler import SchedulerApp

from ..utils.verify_user_callback import VerifyUserCallback
from ..utils.kick_user_job_id_generator import get_kick_user_job_id


if TYPE_CHECKING:
    from aiogram import Bot
    from aiogram.types import CallbackQuery


router = Router(
    name="confirm_btn",
)


@router.callback_query(VerifyUserCallback.filter(F.action == "confirm"))
async def confirm_btn_click_handler(
    event: "CallbackQuery",
    bot: "Bot",
):
    """
    Handle the confirmation button click event.

    Args:
        event (CallbackQuery): The callback query event.
        bot (Bot): The bot instance.

    """
    logger.info(f"Confirm button clicked by: {event.from_user.id}")
    settings = ApplicationSettings()  # type: ignore
    scheduler = SchedulerApp()

    if not event.data:
        logger.warning("No data found in callback query")
        return

    callback_data = VerifyUserCallback.unpack(event.data)

    if callback_data.user_id != event.from_user.id:
        logger.warning(
            f"User ID mismatch: {callback_data.user_id} "
            f"!= {event.from_user.id}",
        )
        await event.answer(
            settings.text_templates.button_click_user_id_mismatch_text,
            show_alert=True,
        )
        return

    if not event.message or isinstance(event.message, InaccessibleMessage):
        logger.warning("No message found in callback query")
        return

    # Cancel scheduled task to kick user
    job_id = get_kick_user_job_id(
        chat_id=event.message.chat.id,
        user_id=event.from_user.id,
    )
    scheduler.cancel_job(job_id)

    await event.answer(
        settings.text_templates.button_click_confirmed_member_text,
        show_alert=True,
    )

    additional_text = ""
    is_restriction_removed = False
    # Restore only send messages permission
    # and set a timeout for 30 seconds
    # after which the user will be able to use all default permissions
    try:
        is_restriction_removed = await bot.restrict_chat_member(
            chat_id=event.message.chat.id,
            user_id=event.from_user.id,
            permissions=ChatPermissions(
                can_send_messages=True,
            ),
            until_date=datetime.now() + timedelta(seconds=30),
        )
        logger.info("User permissions restored successfully")
    except Exception as e:
        logger.error(f"Failed to restore user permissions: {e}")

    if not is_restriction_removed:
        access_dt = (
            event.message.date + timedelta(
                minutes=settings.default_settings.restore_permissions_time,
            )
        )
        additional_text = (
            settings.text_templates.additional_text_for_permissions.format(
                access_dt=access_dt.strftime("%H:%M:%S"),
            )
        )

    try:
        await bot.edit_message_text(
            chat_id=event.message.chat.id,
            message_id=event.message.message_id,
            reply_markup=None,
            text=settings.text_templates.confirmed_member_text.format(
                user=event.from_user.mention_html(),
            ) + additional_text,
        )
        logger.info("Message edited successfully")
    except Exception as e:
        logger.error(f"Failed to edit message: {e}")
