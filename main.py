import sys
import time
from typing import Any

from runner.factory import RUNNER_TYPE, get_runner

runner_type = sys.argv[1].upper() if len(sys.argv) > 1 else RUNNER_TYPE.SUBINTERPRETER
runner = get_runner(runner_type=runner_type)


def callback(
        worker_id: int | None = None,
        result: Any = None
    ) -> None:
    if worker_id:
        print(f'Worker id: {worker_id}, result: {result}')


start = time.time()
runner.start(
    callback=callback
)
end = time.time()
print(f'Run time [s]: {end - start}')
