__all__ = ("SchedulerConfig",)

from pydantic import BaseModel, Field


class SchedulerJobStores(BaseModel):
    """Scheduler job stores settings."""

    file_name: str = Field(
        default="db/scheduler.db",
        description="File name for the SQLite database.",
    )

    @property
    def sqlite_url(self) -> str:
        """
        Get the SQLite URL.

        Returns:
            str: SQLite URL.

        """
        return (
            f"sqlite:///{self.file_name}"
        )


class SchedulerConfig(BaseModel):
    """Scheduler settings for application."""

    jobstores: SchedulerJobStores = SchedulerJobStores()
