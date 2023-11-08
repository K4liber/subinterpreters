import os
from concurrent.futures import ThreadPoolExecutor, wait
from functools import partial
from textwrap import dedent
from typing import Any, Callable

import _xxsubinterpreters as interpreters

import config
from runner.interface import RunnerInterface
from runner.threads import thread_callback


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

                def run(subinterpreter_id: int, callable_index: int) -> int:
                    r, w = os.pipe()
                    interpreters.run_string(
                        subinterpreter_id,
                        dedent(f"""
                        import os
                        import sys
                        sys.path.append(os.getcwd())

                        from job.callables import callables_list

                        result = callables_list[{callable_index}]()

                        with open({w}, 'w', encoding="utf-8") as w_pipe:
                            w_pipe.write(str(result))
                        """)
                    )

                    with os.fdopen(r) as r_pipe:
                        return int(r_pipe.read())
                
                task = executor.submit(partial(run, _subinterpreter_id, _callable_index))
                task.add_done_callback(
                    partial(
                        thread_callback, callback
                    )
                )
                tasks.append(task)

            callback()
            print('Waiting for tasks to complete...')
            wait(tasks)
