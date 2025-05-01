__all__ = ("get_kick_user_job_id",)


def get_kick_user_job_id(
    chat_id: int,
    user_id: int,
) -> str:
    """
    Generate a unique job ID for the kick user job.

    Args:
        chat_id (int): The ID of the chat.
        user_id (int): The ID of the user to be kicked.

    Returns:
        str: A unique job ID for the kick user job.
    """
    return f"kick_{chat_id}_{user_id}"
