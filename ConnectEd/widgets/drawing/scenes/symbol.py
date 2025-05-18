__all__ = ["Symbol"]

from . import Drawing

from ..items import SymbolInstance, Block


class Symbol(Drawing):
    FORBIDDEN_ITEMS = [SymbolInstance, Block]
