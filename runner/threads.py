from concurrent.futures import Future, ThreadPoolExecutor
from functools import partial
from threading import current_thread
from typing import Any, Callable

from config import CALLABLES_LIST
from runner.interface import RunnerInterface


def thread_callback(
        callback: Callable[[int, Any], None],
        future: Future,
    ) -> None:
    if future.exception():
        print(f'Exception: {future.exception()}')

    thread_id = current_thread().getName()[-1]
    callback(thread_id, future.result())


class RunnerThreads(RunnerInterface):
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
        with ThreadPoolExecutor(self._no_workers) as executor:
            for callable in CALLABLES_LIST:
                task = executor.submit(callable)
                task.add_done_callback(
                    partial(
                        thread_callback, callback
                    )
                )

            callback()
            print('Waiting for tasks to complete...')
