__all__ = ("SchedulerApp",)

from typing import TYPE_CHECKING, Callable, Optional

from loguru import logger

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.base import ConflictingIdError, BaseJobStore
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from sqlalchemy import create_engine
from sastb.utils.singleton import Singleton

from .custom_job_executor import AsyncExecutorWithLoggerContext


if TYPE_CHECKING:
    from sastb.config.models.scheduler import SchedulerConfig


class SchedulerApp(metaclass=Singleton):
    """Async Background Scheduler with the desired scheduled functions."""

    __scheduler: "AsyncIOScheduler"
    config: "SchedulerConfig"

    def __init__(self, config: Optional["SchedulerConfig"] = None):
        """
        Initialize the scheduler.

        Args:
            config (SchedulerConfig): The scheduler configuration.

        """
        if not config:
            raise ValueError(
                "Settings are required to initialize the scheduler"
            )

        self.config = config

        engine = create_engine(
            self.config.jobstores.sqlite_url,
        )

        jobstores: dict[str, BaseJobStore] = {
            "default": SQLAlchemyJobStore(
                engine=engine,
            ),
        }

        self.__scheduler = AsyncIOScheduler(
            jobstores=jobstores,
        )

    def get_job(self, job_id: str):
        """
        Get a job with given ID.

        Args:
            job_id (str): id of the job

        Returns:
            Job | None: job object if found, None otherwise

        """
        # Find if job exists
        job = self.__scheduler.get_job(job_id=job_id)
        if not job:
            logger.warning(f"Job {job_id} not found")
            return None

        logger.info(f"Job {job_id} found: {job}")
        return job

    def schedule_job(
        self,
        func: Callable,
        trigger: CronTrigger | IntervalTrigger | DateTrigger,
        job_id: str,
        kwargs: Optional[dict] = None,
        *,
        replace_existing: bool = True,
    ):
        """
        Add a new job to the scheduler.

        Args:
            func (Callable): The function to be scheduled.
            trigger (CronTrigger | IntervalTrigger | DateTrigger): The trigger
                for the job.
            job_id (str): The ID of the job.
            kwargs (dict, optional): Keyword arguments to pass to the function.
            replace_existing (bool, optional): Whether to replace an existing
                job with the same ID.

        Raises:
            ValueError: If the job ID is empty or the function is not callable.

        """
        try:
            job = self.__scheduler.add_job(
                func=func,
                trigger=trigger,
                id=job_id,
                name=job_id,
                kwargs=kwargs,
                replace_existing=replace_existing,
            )
        except ConflictingIdError:
            logger.warning(f"Job {job_id} already exists")
            return

        logger.info(
            f"Added job {job_id}: next_run={job.next_run_time}, "
            f"trigger={job.trigger}"
        )

    def cancel_job(self, job_id: str):
        """
        Remove a job with given ID.

        Args:
            job_id (str): id of the job

        Returns:
            bool: True if job was removed, False otherwise (job not found)

        """
        # Find if job exists
        job = self.__scheduler.get_job(job_id=job_id)
        if not job:
            logger.warning(f"Job {job_id} not found")
            return False

        self.__scheduler.remove_job(job_id=job_id)
        logger.info(f"Removed job {job_id}")
        return True

    def start(self):
        """Start the scheduler."""
        self.__scheduler.add_executor(AsyncExecutorWithLoggerContext())
        self.__scheduler.start()
        logger.info("Scheduler started")

        # Print all restored jobs
        jobs_info = [
            (j.id, j.next_run_time)
            for j in self.__scheduler.get_jobs()
        ]
        logger.info(f"Jobs restored: {jobs_info}")
