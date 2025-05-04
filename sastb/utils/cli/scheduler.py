__all__ = ("start_scheduler",)

from loguru import logger

from sastb.config.config import ApplicationSettings
from sastb.modules.scheduler import SchedulerApp


async def start_scheduler():
    """
    Start the scheduler.
    """
    settings = ApplicationSettings()  # type: ignore

    with logger.contextualize(
        module="scheduler",
    ):
        logger.info("Starting scheduler...")

        scheduler = SchedulerApp(
            config=settings.scheduler,
        )
        logger.info("Scheduler initialized successfully.")

        scheduler.start()
