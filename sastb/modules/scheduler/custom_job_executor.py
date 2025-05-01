__all__ = ("AsyncExecutorWithLoggerContext",)

from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.job import Job

from loguru import logger


class AsyncExecutorWithLoggerContext(AsyncIOExecutor):
    """Custom executor for the APScheduler."""

    @logger.catch()
    def _do_submit_job(self, job: Job, run_times):
        """
        Submit the job to the executor.

        Args:
            job (Job): The job to be submitted.
            run_times (list): The times at which the job should run.

        """
        with logger.contextualize(app="scheduler"):
            return super()._do_submit_job(job, run_times)
