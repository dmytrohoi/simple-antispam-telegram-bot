__all__ = ("Singleton",)

from typing import ClassVar

from threading import Lock


class Singleton(type):
    """Thread-safe implementation of Singleton."""

    _instances: ClassVar[dict] = {}

    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        """
        Create and return the Singleton instance.

        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.

        :return: Singleton instance

        """
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]
