import os
from concurrent.futures import Future, ProcessPoolExecutor
from functools import partial
from multiprocessing import get_context
from typing import Any, Callable

from runner.interface import RunnerInterface, CALLBACK_TYPE

_pids: dict[int, int] = dict()


def _callback(
        callback: CALLBACK_TYPE,
        future: Future,
    ) -> None:
    if future.exception():
        print(f'Exception: {future.exception()}')

    result, pid, memory_usage = future.result()
    
    if pid in _pids:
        worker_id = _pids[pid]
    else:
        _pids[pid] = len(_pids)
        worker_id = _pids[pid]

    if memory_usage:
        callback(worker_id, result, memory_usage)
    else:
        callback(worker_id, result)


def _callable(
    callable: Callable[[], Any]
) -> tuple[Any, int, dict[int, float] | None]:
    result = callable()
    pid = os.getpid()
    return result, pid, RunnerInterface.get_memory_usage(pid=pid)


class RunnerProcesses(RunnerInterface):

    def start(
        self,
        callables_list: list[Callable[[], Any]],
        callback: CALLBACK_TYPE
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
