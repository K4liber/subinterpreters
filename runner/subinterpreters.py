import os
from concurrent.futures import ThreadPoolExecutor
import pickle
from textwrap import dedent
from threading import current_thread
from typing import Any, Callable

import _xxsubinterpreters as interpreters

import config
from runner.interface import RunnerInterface
from job.callables import callables_list


def _run(
        callback,
        subinterpreter_id,
        callable
    ) -> None:
    try:
        result_read_pipe, result_write_pipe = os.pipe()
        callable_read_pipe, callable_write_pipe = os.pipe()

        with open(callable_write_pipe, 'wb') as w_pipe:
            pickle.dump(callable, w_pipe)

        interpreters.run_string(
            subinterpreter_id,
            dedent(f"""
                import os
                import sys
                sys.path.append(os.getcwd())

                import pickle

                with open({callable_read_pipe}, 'rb') as r_pipe:
                    callable = pickle.load(r_pipe)
                
                result = callable()

                with open({result_write_pipe}, 'wb') as w_pipe:
                   pickle.dump(result, w_pipe)

                """
            )
        )
        current_thread_name = current_thread().getName()
        thread_id = current_thread_name[-1]

        with open(result_read_pipe, 'rb') as r_pipe:
            result = pickle.load(r_pipe)
    except Exception as exc:
        callback(-1, str(exc))

    callback(int(thread_id), result)


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
                callable = callables_list[_callable_index]
                executor.submit(_run, callback, _subinterpreter_id, callable)

            callback()
            print('Waiting for tasks to complete...')
