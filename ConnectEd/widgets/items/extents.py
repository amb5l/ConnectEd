from PyQt6.QtCore import QPointF, QRectF

from ...core import settings

from . import RectPenOnlyItem

class Extents(RectPenOnlyItem):
    """Extents of a drawing - the outer limit!"""

    def __init__(self : 'Extents', sheet : str) -> None:
        sheet_size = getattr(settings.sheet_sizes, sheet)
        # 3x width, 3x height of sheet
        super().__init__(
            -QPointF(sheet_size.width(), sheet_size.height()),
            QPointF(sheet_size.width() * 2, sheet_size.height() * 2)
        )
