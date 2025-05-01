__all__ = ("TelegramConfig",)

from pydantic import BaseModel, Field


class BotInfo(BaseModel):
    """Bot information."""

    description: str = Field(
        default=(
            "The source code ot this bot is available at "
            "https://github.com/dmytrohoi/simple-antispam-telegram-bot\n\n"
            "You can also use more advanced variant of this bot - "
            "@advancedguardbot."
        ),
        max_length=200,
        description="Description of the bot",
    )
    short_description: str = Field(
        default=(
            "Source code - "
            "https://github.com/dmytrohoi/simple-antispam-telegram-bot\n\n"
            "Also check - @advancedguardbot."
        ),
        max_length=120,
        description="Short description of the bot",
    )


class TelegramConfig(BaseModel):
    """Telegram bot settings."""

    token: str = Field(..., description="Telegram bot token")

    # Server settings
    host: str = Field("0.0.0.0", description="Host for the bot")
    port: int = Field(8080, description="Port for the bot")
    webhook_path: str = Field(
        "/bots/satb/webhook",
        description="Webhook path for the bot",
    )
    webhook_secret_token: str = Field(
        "so-secret-token",
        description="Webhook secret token for the bot",
    )
    webhook_base_url: str = Field(
        ...,
        description="Webhook base URL for the bot",
    )
    info: BotInfo = BotInfo()

    @property
    def webhook_url(self) -> str:
        """
        Generate the webhook URL for the bot.
        """
        return f"{self.webhook_base_url}{self.webhook_path}"
