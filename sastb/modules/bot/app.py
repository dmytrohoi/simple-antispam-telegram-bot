__all__ = ("BotApp",)

from typing import TYPE_CHECKING, Optional

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.types.chat_administrator_rights import ChatAdministratorRights
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application,
)
from aiohttp import web
from loguru import logger

from sastb.utils.singleton import Singleton

from . import routes
from .utils.exceptions import SetupError

if TYPE_CHECKING:
    from sastb.config.models.telegram import TelegramConfig


class BotApp(metaclass=Singleton):
    """BotApp class for the bot."""

    bot: "Bot"
    dispatcher: "Dispatcher"
    config: "TelegramConfig"

    def __init__(self, config: Optional["TelegramConfig"] = None):
        """ "
        Initialize the bot app.

        Args:
            token (str): The bot token.

        """
        if not config:
            raise ValueError("config cannot be None")

        self.config = config

        session = AiohttpSession()
        self.bot = Bot(
            self.config.token,
            session=session,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        self.dispatcher = Dispatcher()

    async def on_startup(self, dispatcher: Dispatcher, bot: Bot):
        try:
            result = await self.bot.set_webhook(
                url=self.config.webhook_url,
                secret_token=self.config.webhook_secret_token,
                allowed_updates=[
                    "chat_member",
                    "my_chat_member",
                    "callback_query",
                ]
            )
            logger.info(f"Webhook set: {result} to {self.config.webhook_url}")
            result = await self.bot.set_my_short_description(
                short_description=self.config.info.short_description,
            )
            logger.info(f"Short description set: {result}")
            result = await self.bot.set_my_description(
                description=self.config.info.description,
            )
            logger.info(f"Description set: {result}")
            result = await self.bot.set_my_default_administrator_rights(
                rights=ChatAdministratorRights(
                    # Required permissions
                    can_restrict_members=True,
                    # Other to False
                    is_anonymous=False,
                    can_manage_chat=False,
                    can_delete_messages=False,
                    can_manage_video_chats=False,
                    can_promote_members=False,
                    can_change_info=False,
                    can_invite_users=False,
                    can_post_stories=False,
                    can_edit_stories=False,
                    can_delete_stories=False,
                ),
            )
            logger.info(f"Default administrator rights set: {result}")
        except Exception as setup_error:
            logger.error(f"Error on startup: {setup_error}")
            raise SetupError from setup_error

    async def start(self):
        """Start the bot."""
        self.dispatcher.include_routers(
            routes.bot_member_handler,
            routes.confirm_btn_handler,
            routes.member_join_handler,
            routes.member_left_handler,
        )

        self.dispatcher.startup.register(self.on_startup)

        app = web.Application()

        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=self.dispatcher,
            bot=self.bot,
            secret_token=self.config.webhook_secret_token,
        )
        webhook_requests_handler.register(app, path=self.config.webhook_path)

        setup_application(app, self.dispatcher, bot=self.bot)

        while True:
            try:
                await web._run_app(
                    app,
                    host=self.config.host,
                    port=self.config.port,
                )
            except KeyboardInterrupt:
                logger.warning("Stopping bot...")
                break
            except SetupError:
                logger.error("Setup error occurred. Retrying...")
                break
            except Exception as e:
                logger.error(f"Error starting bot: {e}")
            finally:
                await self.bot.session.close()
                logger.info("Bot stopped.")
