__all__ = ['Symbol']

from types import NoneType

from .scenes import Drawing


class Symbol(Drawing):
    _TYPES = [NoneType]
