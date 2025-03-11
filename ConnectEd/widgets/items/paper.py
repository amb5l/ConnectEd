from PyQt6.QtCore    import QPointF

from ...core import Z_PAPER, settings

from . import RectBrushOnlyItem


class Paper(RectBrushOnlyItem):
    Z = Z_PAPER

    size_name : str

    def __init__(self : 'Paper', size : str):
        super().__init__()
        self.setSize(size)
        self.setZValue(Z_PAPER)

    def setSize(self : 'Paper', size_name : str) -> None:
        self.size_name = size_name
        self.setPoints(
            QPointF(0, 0),
            getattr(settings.sheet_sizes, size_name)
        )
