import os
from concurrent.futures import Future, ProcessPoolExecutor
from functools import partial
from multiprocessing import get_context
from typing import Any, Callable

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

    def start(
        self,
        callables_list: list[Callable[[], Any]],
        callback: Callable[[int, Any], Any]
    ) -> None:
        mp_context = get_context('spawn')  # Force the same context on both Unix and Windows

        with ProcessPoolExecutor(self._no_workers, mp_context=mp_context) as executor:
            for callable in callables_list:
                task = executor.submit(partial(_callable, callable))
                task.add_done_callback(
                    partial(
                        _callback, callback
                    )
                )
        
            callback()

        global _pids
        _pids = dict()
