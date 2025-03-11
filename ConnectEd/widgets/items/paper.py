from PyQt6.QtCore    import QPointF

from ...core import Z_PAPER, settings

from . import RectBrushOnlyItem


class Paper(RectBrushOnlyItem):
    Z = Z_PAPER

    size_name : str

    def __init__(self : 'Paper', size : str):
        super().__init__(QPointF(0, 0))
        self.setZValue(Z_PAPER)
        self.setSize(size)

    def setSize(self : 'Paper', size_name : str) -> None:
        self.size_name = size_name
        size = getattr(settings.sheet_sizes, size_name)
        self.setPoints(
            QPointF(0, 0),
            QPointF(size.width(), size.height())
        )
