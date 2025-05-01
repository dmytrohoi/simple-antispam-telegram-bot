__all__ = ("router",)

from loguru import logger

from aiogram import Bot, Router
from aiogram.types import ChatMemberUpdated
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter
from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER

from sastb.config.config import ApplicationSettings


router = Router(
    name="bot_member",
)


@router.my_chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def bot_join_handler(
    event: "ChatMemberUpdated",
    bot: "Bot",
):
    """
    Handle the event when the bot joins a chat.

    Args:
        event (ChatMemberUpdated): The event object containing information
            about the member who joined.
        bot (Bot): The bot instance.

    """
    settings = ApplicationSettings()  # type: ignore

    logger.info(f"New member: {event.new_chat_member.user.id}")

    if not settings.administrators:
        logger.warning("No administrators set, skipping...")
        return

    if event.from_user.id not in settings.administrators:
        logger.warning(
            f"User {event.from_user.id} is not an administrator, skipping..."
        )
        await event.answer(
            text=settings.text_templates.invited_not_by_admin_text.format(
                user=event.from_user.mention_html(),
            ),
        )

        await bot.leave_chat(
            chat_id=event.chat.id,
        )
        logger.info("Bot left the chat")
        return

    await event.answer(
        text=settings.text_templates.invited_by_admin_text.format(
            user=event.from_user.mention_html(),
        ),
    )
    logger.info(f"Bot joined the chat with id: {event.chat.id}")
