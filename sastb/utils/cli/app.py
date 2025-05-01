__all__ = ("click_app",)

import asyncio
from functools import wraps
from click import Group

import uvloop


click_app = Group(
    name="simple-antispam-telegram-bot",
    help="Simple AntiSpam Telegram Bot CLI",
    invoke_without_command=True,
    no_args_is_help=True,
    add_help_option=True,
)


def awaitable(f):
    """Allow using async functions in commands."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        """
        Wrap async function run.

        :param args: list of arguments
        :param kwargs: dict of arguments

        """
        with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
            return runner.run(f(*args, **kwargs))

    return wrapper


@click_app.command(name="start", help="Start the bot")
@awaitable
async def start():
    """
    Start the bot.
    """
    from .setup_logging import setup_logging

    setup_logging()

    from .bot import start_bot
    from .scheduler import start_scheduler

    await asyncio.gather(
        start_bot(),
        start_scheduler(),
    )
