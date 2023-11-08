import os
from concurrent.futures import Future, ThreadPoolExecutor
from functools import partial
from textwrap import dedent
from threading import current_thread
from typing import Any, Callable

import _xxsubinterpreters as interpreters

import config
from runner.interface import RunnerInterface


def subinterpreter_callback(
        callback: Callable[[int, Any], None],
        r,
        future: Future
    ) -> None:
    if future.exception():
        print(f'Exception: {future.exception()}')

    with os.fdopen(r) as r_pipe:
        result = int(r_pipe.read())
    
    thread_id = current_thread().getName()[-1]
    callback(thread_id, result)


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

        with ThreadPoolExecutor(self._no_workers) as executor:
            for _callable_index in range(config.NUMBER_OF_JOBS):
                _subinterpreter_id = subinterpreter_ids[_callable_index]
                r, _w = os.pipe()
            
                def run(subinterpreter_id: int, callable_index: int, w) -> int:
                    interpreters.run_string(
                        subinterpreter_id,
                        dedent(f"""
                        import os
                        import sys
                        sys.path.append(os.getcwd())

                        from config import CALLABLES_LIST

                        result = CALLABLES_LIST[{callable_index}]()

                        with open({w}, 'w', encoding="utf-8") as w_pipe:
                            w_pipe.write(str(result))
                        """)
                    )
                
                task = executor.submit(partial(run, _subinterpreter_id, _callable_index, _w))
                task.add_done_callback(
                    partial(
                        subinterpreter_callback, callback, r
                    )
                )

            callback()
            print('Waiting for tasks to complete...')
