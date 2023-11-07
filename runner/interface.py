from abc import ABCMeta, abstractmethod
from typing import Any, Callable


class RunnerInterface(metaclass=ABCMeta):
    def __init__(
        self,
        no_workers: int
    ):
        self._no_workers = no_workers

    @abstractmethod
    def start(
        self,
        callables: list[Callable[[], Any]],
        callback: Callable[[int, Any], Any]
    ) -> None:
        ...
