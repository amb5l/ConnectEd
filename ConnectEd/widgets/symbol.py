__all__ = [
    'Symbol'
]

from types import NoneType

from .drawing import Drawing


class Symbol(Drawing):
    _TYPES = [NoneType]
