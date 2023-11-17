from concurrent.futures import Future, ThreadPoolExecutor, wait
from functools import partial
from threading import current_thread
from typing import Any, Callable

from runner.interface import RunnerInterface


def thread_callback(
        callback: Callable[[int, Any], None],
        future: Future,
    ) -> None:
    if future.exception():
        print(f'Exception: {future.exception()}')

    thread_id = current_thread().getName()[-1]

    try:
        thread_id = int(thread_id)
    except ValueError:
        thread_id = 0

    callback(thread_id, future.result())


class RunnerThreads(RunnerInterface):
    def __init__(
        self,
        no_workers: int
    ) -> None:
        super().__init__(no_workers=no_workers)

    def start(
        self,
        callables_list: list[Callable[[], Any]],
        callback: Callable[[int, Any], Any]
    ) -> None:
        print(f'Running with {self._no_workers} workers.')
        tasks = []

        with ThreadPoolExecutor(self._no_workers) as executor:
            for callable in callables_list:
                task = executor.submit(callable)
                task.add_done_callback(
                    partial(
                        thread_callback, callback
                    )
                )
                tasks.append(task)

            callback()
            print('Waiting for tasks to complete...')
            wait(tasks)
