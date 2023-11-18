from dataclasses import dataclass
from typing import Callable

from task.fibonacci import fibonacci
from task.test_numpy import test_numpy

@dataclass(frozen=True)
class _Callables:
    FIBONACCI: str = 'FIBONACCI'
    TEST_NUMPY: str = 'TEST NUMPY'


CALLABLES = _Callables()

_name_to_callable  = {
    CALLABLES.FIBONACCI: fibonacci,
    CALLABLES.TEST_NUMPY: test_numpy
}

def get_available_callables() -> list[str]:
    return list(_name_to_callable.keys())


def get_callable(callable_name: str) -> Callable:
    return _name_to_callable[callable_name] 
