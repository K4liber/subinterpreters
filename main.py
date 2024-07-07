from functools import partial
import sys
import time
from typing import Any
import config

from runner.factory import RUNNER_TYPE, get_runner

from job.callables import get_callable, CALLABLES

runner_type = \
    sys.argv[1].upper() \
    if len(sys.argv) > 1 \
    else RUNNER_TYPE.THREAD
runner = get_runner(runner_type=runner_type)
selected_function = \
    get_callable(sys.argv[2]) \
    if len(sys.argv) > 2 \
    else get_callable(CALLABLES.FIBONACCI)
function_args = \
    sys.argv[3:] \
    if len(sys.argv) > 3 \
    else [34]

def _callback(
        worker_id: int | None = None,
        result: Any = None
    ) -> None:
    if worker_id is None:
        print(f'Execution started with runner {runner_type}')
    else:
        print(f'Worker id: {worker_id}, result: {result}')


start = time.time()
runner.start(
    callables_list=[
        partial(selected_function, *function_args)
        for _ in range(config.NUMBER_OF_JOBS)
    ],
    callback=_callback
)
end = time.time()
print(f'Run time [s]: {end - start}')
