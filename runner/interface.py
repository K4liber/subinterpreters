from abc import ABCMeta, abstractmethod
from typing import Any, Callable


class RunnerInterface(metaclass=ABCMeta):
    def __init__(
        self,
        no_workers: int,
        runner_type: str
    ):
        self._no_workers = no_workers
        self._runner_type = runner_type

    @abstractmethod
    def start(
        self,
        callables_list: list[Callable[[], Any]],
        callback: Callable[[int, Any], Any]
    ) -> None:
        ...
    
    @property
    def no_workers(self) -> int:
        return self._no_workers

    @property
    def runner_type(self) -> str:
        return self._runner_type
