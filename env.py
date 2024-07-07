from dataclasses import dataclass
import sys


@dataclass(frozen=True)
class _ENV:
    PYTHON_313: bool


ENV = _ENV(
    PYTHON_313=sys.version_info >= (3, 13)
)
