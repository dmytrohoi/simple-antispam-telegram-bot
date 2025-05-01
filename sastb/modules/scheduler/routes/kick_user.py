__all__ = ("kick_user_job",)

from loguru import logger

from aiogram.utils.chat_member import NOT_MEMBERS


async def kick_user_job(
    chat_id: int,
    user_id: int,
    message_id: int,
):
    """
    Kick user from chat.

    Args:
        chat_id (int): The ID of the chat.
        user_id (int): The ID of the user to be kicked.
        message_id (int): The ID of the message to be edited.

    """
    from sastb.config import ApplicationSettings
    from sastb.modules.bot import BotApp

    bot = BotApp().bot
    settings = ApplicationSettings()  # type: ignore

    logger.info(f"Kicking user {user_id} from chat {chat_id}")
    chat_member = None
    try:
        chat_member = await bot.get_chat_member(
            chat_id=chat_id,
            user_id=user_id,
        )
    except Exception as get_chat_member_exc:
        logger.warning(
            f"Error getting chat member {user_id}: {get_chat_member_exc}"
        )

    if chat_member is None or isinstance(chat_member, NOT_MEMBERS):
        logger.info(f"User {user_id} already left the chat")
        try:
            await bot.delete_message(
                chat_id=chat_id,
                message_id=message_id,
            )
            logger.info(f"Message deleted: {message_id}")
        except Exception as delete_message_exc:
            logger.error(f"Failed to delete message: {delete_message_exc}")
        return

    try:
        await bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
        logger.info(f"User {user_id} kicked from chat {chat_id}")
    except Exception as kick_user_exc:
        logger.error(f"Failed to kick user {user_id}: {kick_user_exc}")
        await bot.send_message(
            chat_id=chat_id,
            text=settings.text_templates.kick_user_error_text.format(
                user=chat_member.user.mention_html(),
            ),
        )
        return

    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=settings.text_templates.kicked_user_text.format(
                user=chat_member.user.mention_html(),
            ),
            reply_markup=None,
        )
        logger.info(f"Message edited: {message_id}")
    except Exception as edit_message_exc:
        logger.error(f"Failed to edit message: {edit_message_exc}")
