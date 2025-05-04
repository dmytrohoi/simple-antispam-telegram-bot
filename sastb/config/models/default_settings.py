__all__ = ("DefaultSettings",)

from pydantic import BaseModel, Field


class DefaultSettings(BaseModel):
    """Default settings for the bot."""

    remove_user_after: int = Field(
        default=5,
        description="Time in minutes to remove user after confirmation",
    )
    additional_delay_for_permissions: int = Field(
        default=2,
        description=(
            "Time in minutes to delay for permissions that adds to "
            "remove_user_after time"
        ),
    )

    @property
    def restore_permissions_time(self) -> int:
        """
        Calculate the time in minutes to restore permissions.
        """
        return self.remove_user_after + self.additional_delay_for_permissions
