from dataclasses import dataclass

import config
from runner.interface import RunnerInterface
from runner.processes import RunnerProcesses
from runner.subinterpreters import RunnerSubinterpreters
from runner.threads import RunnerThreads


@dataclass(frozen=True)
class _RunnerType:
    THREAD = 'THREAD'
    PROCESS = 'PROCESS'
    SUBINTERPRETER = 'SUBINTERPRETER'


RUNNER_TYPE = _RunnerType()

def get_runner(
        runner_type: str
    ) -> RunnerInterface:
    runner_class = {
        RUNNER_TYPE.THREAD: RunnerThreads,
        RUNNER_TYPE.PROCESS: RunnerProcesses,
        RUNNER_TYPE.SUBINTERPRETER: RunnerSubinterpreters
    }.get(runner_type)
    return runner_class(
        no_workers=config.NUMBER_OF_WORKERS
    )
