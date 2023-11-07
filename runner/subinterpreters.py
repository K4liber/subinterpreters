import _xxsubinterpreters as interpreters
from typing import Any, Callable
from runner.interface import RunnerInterface


class RunnerSubinterpreters(RunnerInterface):
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
        subinterpreter_ids = [
            interpreters.create()
            for _ in range(self._no_workers)
        ]

        for index, callable in enumerate(callables):
            subinterpreter_index = index % self._no_workers
            subinterpreter_id = subinterpreter_ids[subinterpreter_index]
            print(f'Submitting task {index} to subinterpreter {subinterpreter_id}')
            interpreters.run_string(
                subinterpreter_id,
                "import os; import sys; sys.path.append(os.getcwd()); from task.fibonacci import fibonacci; fibonacci(35)"
            )
