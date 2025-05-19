__all__ = ["SymbolScene"]

from . import DrawingScene

from ..items import SymbolInstance, Block


class SymbolScene(DrawingScene):
    FORBIDDEN_ITEMS = [SymbolInstance, Block]
