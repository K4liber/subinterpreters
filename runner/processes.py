import os
from concurrent.futures import Future, ProcessPoolExecutor
from functools import partial
from multiprocessing import get_context
from typing import Any, Callable

from config import CALLABLES_LIST
from runner.interface import RunnerInterface

_pids: dict[int, int] = dict()


def _callback(
        callback: Callable[[int, Any], None],
        future: Future,
    ) -> None:
    if future.exception():
        print(f'Exception: {future.exception()}')

    result, pid = future.result()
    
    if pid in _pids:
        worker_id = _pids[pid]
    else:
        _pids[pid] = len(_pids)
        worker_id = _pids[pid]

    callback(worker_id, result)


def _callable(
    callable: Callable[[], Any]
) -> tuple[Any, int]:
    result = callable()
    return result, os.getpid()


class RunnerProcesses(RunnerInterface):
    def __init__(
        self,
        no_workers: int
    ) -> None:
        super().__init__(no_workers=no_workers)

    def start(
        self,
        callback: Callable[[int, Any], Any]
    ) -> None:
        print(f'Running with {self._no_workers} workers.')
        tasks = []
        mp_context = get_context('spawn')  # Force the same context on both Unix and Windows
        executor = ProcessPoolExecutor(self._no_workers, mp_context=mp_context)

        for callable in CALLABLES_LIST:
            task = executor.submit(_callable, callable)
            task.add_done_callback(
                partial(
                    _callback, callback
                )
            )
            tasks.append(task)

        callback()
        print('Waiting for tasks to complete...')
        executor.shutdown(wait=True)
        global _pids
        _pids = dict()
