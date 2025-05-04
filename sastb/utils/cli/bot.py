__all__ = ("start_bot",)

from loguru import logger

from sastb.config.config import ApplicationSettings
from sastb.modules.bot import BotApp


async def start_bot():
    """
    Start the bot.
    """
    settings = ApplicationSettings()  # type: ignore

    with logger.contextualize(
        module="bot",
    ):
        logger.info("Starting bot...")

        bot = BotApp(
            config=settings.telegram,
        )
        logger.info("Bot initialized successfully.")

        await bot.start()
