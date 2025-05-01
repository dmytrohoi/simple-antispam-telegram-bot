__all__ = ("router",)

from datetime import timedelta
from loguru import logger

from aiogram import Bot, Router
from aiogram.types import (
    ChatMemberUpdated,
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.chat_member import ADMINS
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter
from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER

from apscheduler.triggers.interval import IntervalTrigger

from sastb.config.config import ApplicationSettings
from sastb.modules.scheduler import SchedulerApp
from sastb.modules.scheduler.routes import kick_user_job

from ..utils.verify_user_callback import VerifyUserCallback
from ..utils.kick_user_job_id_generator import get_kick_user_job_id


router = Router(
    name="member_join",
)


@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def member_join_handler(
    event: "ChatMemberUpdated",
    bot: "Bot",
):
    """
    Handle member join event.

    Args:
        event (ChatMemberUpdated): The event object containing information
            about the member who joined.
        bot (Bot): The bot instance.

    """
    settings = ApplicationSettings()  # type: ignore
    scheduler = SchedulerApp()

    logger.info(f"New member: {event.new_chat_member.user.id}")

    if event.new_chat_member.user.is_bot:
        logger.info("Member is a bot, skipping...")
        return

    if isinstance(event.new_chat_member, ADMINS):
        # Handle new member
        logger.info("Member is admin, skipping...")
        return

    if settings.default_settings.additional_delay_for_permissions:
        try:
            result = await bot.restrict_chat_member(
                chat_id=event.chat.id,
                user_id=event.new_chat_member.user.id,
                permissions=ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_polls=False,
                    can_send_other_messages=False,
                    can_add_web_page_previews=False,
                    can_change_info=False,
                    can_invite_users=False,
                    can_pin_messages=False,
                    can_manage_chat=False,
                ),
                until_date=event.date + timedelta(
                    minutes=settings.default_settings.restore_permissions_time,
                ),
            )
            logger.info(f"User access has been restricted: {result}")
        except Exception as e:
            logger.error(f"Failed to restrict user: {e}")

    # Send welcome message and start scheduled task to kick user
    new_message = await event.answer(
        text=settings.text_templates.welcome_message_text.format(
            user=event.new_chat_member.user.mention_html(),
        ),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(
                    text=settings.text_templates.confirm_button_text,
                    callback_data=VerifyUserCallback(
                        user_id=event.new_chat_member.user.id
                    ).pack()
                ),
            ]],
        ),
    )
    logger.info(f"Welcome message sent: {new_message.message_id}")

    # Schedule task to kick user after 5 minutes
    job_id = get_kick_user_job_id(
        chat_id=event.chat.id,
        user_id=event.new_chat_member.user.id,
    )
    scheduler.schedule_job(
        job_id=job_id,
        func=kick_user_job,
        kwargs={
            "chat_id": event.chat.id,
            "user_id": event.new_chat_member.user.id,
            "message_id": new_message.message_id,
        },
        trigger=IntervalTrigger(
            minutes=settings.default_settings.remove_user_after,
        ),
    )
    logger.info(f"Scheduled job: {job_id}")
