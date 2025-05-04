__all__ = ("TemplatesSettings",)

from pydantic import BaseModel, Field


class TemplatesSettings(BaseModel):
    """Default settings for the bot."""

    welcome_message_text: str = Field(
        default="Welcome {user}!\nPlease click button below ⤵️",
        description="Welcome message for new members",
    )
    confirm_button_text: str = Field(
        default="I'm not a bot",
        description="Text for the confirmation button in the welcome message",
    )
    confirmed_member_text: str = Field(
        default="Welcome {user}!\nYou are now a member.",
        description="Text for the confirmation button in the welcome message",
    )
    user_left_text: str = Field(
        default="User {user} has left the group.",
        description="Text for the confirmation button in the welcome message",
    )
    kicked_user_text: str = Field(
        default="{user} has been kicked from the group.",
        description="Text for the confirmation button in the welcome message",
    )
    kick_user_error_text: str = Field(
        default="Failed to kick {user} from the group.",
        description="Text for the confirmation button in the welcome message",
    )
    additional_text_for_permissions: str = Field(
        default=(
            "\n\n<i><b>NOTE:</b>\nAccess to the group will be granted after "
            "{access_dt}</i>"
        ),
        description="Additional text for permissions",
    )
    button_click_user_id_mismatch_text: str = Field(
        default="It seems you are not the one who should confirm this action.",
        description="Text for the confirmation button in the welcome message",
    )
    button_click_confirmed_member_text: str = Field(
        default="You have confirmed your membership.",
        description="Text for the confirmation button in the welcome message",
    )
    invited_not_by_admin_text: str = Field(
        default=(
            "I can't start to work in this group, because I was invited "
            "by someone who is not an administrator. 😢"
        ),
        description="Text for invited not by admin",
    )
    invited_by_admin_text: str = Field(
        default="I will start to work in this group. 😊",
        description="Text for invited by admin",
    )
