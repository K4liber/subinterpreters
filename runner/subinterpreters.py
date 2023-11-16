import os
from concurrent.futures import ThreadPoolExecutor, wait
from textwrap import dedent
from threading import current_thread
from typing import Any, Callable

import _xxsubinterpreters as interpreters

import config
from runner.interface import RunnerInterface


def run(_callback, _subinterpreter_id, callable_index) -> None:
    r_pipe, w_pipe = os.pipe()
    interpreters.run_string(
    _subinterpreter_id,
    dedent(f"""
        import os
        import sys
        sys.path.append(os.getcwd())

        from job.callables import callables_list

        result = callables_list[{callable_index}]()

        with open({w_pipe}, 'w', encoding="utf-8") as w_pipe:
            w_pipe.write(str(result))
        """)
    )
    current_thread_name = current_thread().getName()
    print(current_thread_name)
    thread_id = current_thread_name[-1]

    with os.fdopen(r_pipe) as r:
        result = int(r.read())

    _callback(int(thread_id), result)


class RunnerSubinterpreters(RunnerInterface):
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
        subinterpreter_ids = [
            interpreters.create()
            for _ in range(config.NUMBER_OF_JOBS)
        ]
        tasks = []

        with ThreadPoolExecutor(self._no_workers) as executor:
            for _callable_index in range(config.NUMBER_OF_JOBS):
                _subinterpreter_id = subinterpreter_ids[_callable_index]
                task = executor.submit(run, callback, _subinterpreter_id, _callable_index)
                tasks.append(task)

            callback()
            print('Waiting for tasks to complete...')
            wait(tasks)
