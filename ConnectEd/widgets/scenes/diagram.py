__all__ = ['Diagram']

from . import Drawing

from ..items import Paper, Border

class Diagram(Drawing):
    SYSTEM_ALLOWED_ITEMS = Drawing.SYSTEM_ALLOWED_ITEMS + [Paper, Border]
