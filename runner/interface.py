from abc import ABCMeta, abstractmethod
import os
from typing import Any, Callable

from env import ENV

import psutil

CALLBACK_TYPE = Callable[[int, Any, dict | None], Any]

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
        callback: CALLBACK_TYPE
    ) -> None:
        ...
    
    @property
    def no_workers(self) -> int:
        return self._no_workers

    @property
    def runner_type(self) -> str:
        return self._runner_type
    
    @staticmethod
    def get_memory_usage(pid: int | None = None) -> dict[int, float] | None:
        if not ENV.PYTHON_313:
            pid = pid if pid is not None else os.getpid()
            process = psutil.Process(pid=pid)
            return {pid: process.memory_info().rss / 1024 ** 2}
        else:
            raise NotImplementedError(f'get_memory_usage() not implemented for python3.13')
