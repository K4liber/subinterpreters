from functools import partial

from task.fibonacci import fibonacci


NUMBER_OF_WORKERS = 10
NUMBER_OF_JOBS = 50
CALLABLES_LIST = [
    partial(fibonacci, 32) for _ in range(NUMBER_OF_JOBS)
]
