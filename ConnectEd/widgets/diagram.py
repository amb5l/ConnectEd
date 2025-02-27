from types import NoneType

from ..core   import TypedList
from .drawing import Drawing
from .symbol  import Symbol


class Diagram(Drawing):
    ELEMENT_TYPES = [NoneType]
    size    : str
    border  : int
    symbols : TypedList[Symbol]
