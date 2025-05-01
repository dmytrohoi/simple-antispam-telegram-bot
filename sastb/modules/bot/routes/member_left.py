__all__ = ("router",)

from loguru import logger

from aiogram import Bot, Router
from aiogram.types import (
    ChatMemberUpdated,
)
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter
from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER

from apscheduler.job import Job

from sastb.config import ApplicationSettings
from sastb.modules.scheduler import SchedulerApp

from ..utils.kick_user_job_id_generator import get_kick_user_job_id


router = Router(
    name="member_left",
)


@router.chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def member_left_handler(
    event: "ChatMemberUpdated",
    bot: "Bot",
):
    """
    Handle member left event.

    Args:
        event (ChatMemberUpdated): The event object containing information
            about the member who left.
        bot (Bot): The bot instance.

    """
    settings = ApplicationSettings()  # type: ignore
    scheduler = SchedulerApp()

    logger.info(f"Member left: {event.new_chat_member.user.id}")
    job: Job | None = scheduler.get_job(
        job_id=get_kick_user_job_id(
            chat_id=event.chat.id,
            user_id=event.new_chat_member.user.id,
        )
    )
    if not job:
        logger.info("Job not found, skipping...")
        return

    scheduler.cancel_job(job_id=job.id)
    logger.info(f"Job removed: {job.id}")

    message_id = job.kwargs["message_id"]
    is_message_deleted = False
    try:
        is_message_deleted = await bot.delete_message(
            chat_id=event.chat.id,
            message_id=message_id,
        )
        logger.info(f"Message deleted: {message_id}")
    except Exception as e:
        logger.error(f"Failed to delete message: {e}")

    if not is_message_deleted:
        try:
            await bot.edit_message_text(
                text=settings.text_templates.user_left_text.format(
                    user=event.old_chat_member.user.mention_html(),
                ),
                chat_id=event.chat.id,
                message_id=message_id,
                reply_markup=None,
            )
            logger.info(f"Message edited: {message_id}")
        except Exception as e:
            logger.error(f"Failed to edit message: {e}")
