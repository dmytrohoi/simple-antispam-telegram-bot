__all__ = ("ApplicationSettings",)

from typing import Annotated

from pydantic import field_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict, NoDecode

from .models.default_settings import DefaultSettings
from .models.scheduler import SchedulerConfig
from .models.telegram import TelegramConfig
from .models.templates import TemplatesSettings


class Settings(BaseSettings):
    """
    Application settings for the Simple AntiSpam Telegram Bot.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        env_prefix="sastb_",
        case_sensitive=True,
        extra="ignore",
    )

    administrators: Annotated[list[int], NoDecode] = Field(
        default_factory=list,
        description="List of administrator IDs",
    )

    telegram: TelegramConfig
    scheduler: SchedulerConfig = SchedulerConfig()
    default_settings: DefaultSettings = DefaultSettings()
    text_templates: TemplatesSettings = TemplatesSettings()

    @field_validator('administrators', mode='before')
    @classmethod
    def decode_administrators(cls, v: str) -> list[int]:
        return [int(x) for x in v.split(',') if x]



class ApplicationSettings(Settings):
    """Application settings for the Simple AntiSpam Telegram Bot."""

    def __new__(cls, *args, **kwargs):
        """
        Create a new instance of the ApplicationSettings class.
        """
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance
