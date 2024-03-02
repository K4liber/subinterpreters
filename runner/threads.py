from concurrent.futures import Future, ThreadPoolExecutor
from functools import partial
from threading import current_thread
from typing import Any, Callable

from runner.interface import RunnerInterface, CALLBACK_TYPE


def thread_callback(
        callback: CALLBACK_TYPE,
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

    def start(
        self,
        callables_list: list[Callable[[], Any]],
        callback: CALLBACK_TYPE
    ) -> None:

        with ThreadPoolExecutor(self._no_workers) as executor:
            for callable in callables_list:
                task = executor.submit(callable)
                task.add_done_callback(
                    partial(
                        thread_callback, callback
                    )
                )

            callback()
