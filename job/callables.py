from dataclasses import dataclass
from typing import Callable

from task.fibonacci import fibonacci

@dataclass(frozen=True)
class _Callables:
    FIBONACCI: str = 'FIBONACCI'


CALLABLES = _Callables()

_name_to_callable  = {
    CALLABLES.FIBONACCI: fibonacci
}

def get_available_callables() -> list[str]:
    return list(_name_to_callable.keys())


def get_callable(callable_name: str) -> Callable:
    return _name_to_callable[callable_name] 
