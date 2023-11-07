from functools import partial
from typing import Any
from runner.factory import get_runner
import sys

runner_type = sys.argv[1].upper()
runner = get_runner(runner_type=runner_type)


def fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("Incorrect input")
    elif n == 0:
        return 0
    elif n == 1 or n == 2:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)


tasks = [partial(fibonacci, 30) for _ in range(40)]


def callback(worker_id: int, result: Any) -> None:
    print(f'Worker id: {worker_id}, result: {result}')


runner.start(
    callables=tasks,
    callback=callback
)
