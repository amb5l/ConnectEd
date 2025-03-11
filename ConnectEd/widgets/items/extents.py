from PyQt6.QtCore import QPointF, QRectF

from ...core import settings, Z_EXTENTS

from . import RectPenOnlyItem

class Extents(RectPenOnlyItem):
    """Extents of a drawing - the outer limit!"""

    Z = Z_EXTENTS

    def __init__(self : 'Extents', sheet : str) -> None:
        sheet_size = getattr(settings.sheet_sizes, sheet)
        p1 = -QPointF(sheet_size.width(), sheet_size.height())
        p2 = QPointF(sheet_size.width() * 2, sheet_size.height() * 2)
        super().__init__(p1, p2)
