from dataclasses import dataclass
from typing import Callable

from env import ENV
from task.fibonacci import fibonacci


@dataclass(frozen=True)
class _Callables:
    FIBONACCI: str = 'FIBONACCI'
    TEST_NUMPY: str = 'TEST NUMPY'


CALLABLES = _Callables()

_name_to_callable  = {
    CALLABLES.FIBONACCI: fibonacci
}

if not ENV.PYTHON_313:
    from task.test_numpy import test_numpy
    _name_to_callable[CALLABLES.TEST_NUMPY] = test_numpy


def get_available_callables() -> list[str]:
    return list(_name_to_callable.keys())


def get_callable(callable_name: str) -> Callable:
    return _name_to_callable[callable_name] 
