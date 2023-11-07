from concurrent.futures import Future, ProcessPoolExecutor
from functools import partial
from typing import Any, Callable
from runner.interface import RunnerInterface

import os

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
        callables: list[Callable[[], Any]],
        callback: Callable[[int, Any], Any]
    ) -> None:
        print(f'Running with {self._no_workers} workers.')

        with ProcessPoolExecutor(self._no_workers) as executor:
            # call a function on each item in a list and handle results
            for callable in callables:
                print(f'Calling ...')
                task = executor.submit(partial(_callable, callable))
                task.add_done_callback(
                    partial(
                        _callback, callback
                    )
                )
