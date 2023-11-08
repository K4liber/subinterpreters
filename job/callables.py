from functools import partial
import config

from task.fibonacci import fibonacci


callables_list = [
    partial(fibonacci, 32) for _ in range(config.NUMBER_OF_JOBS)
]
