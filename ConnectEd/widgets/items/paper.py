__all__ = ['Paper']

from PyQt6.QtCore    import QPointF, QSizeF

from ...core import Z_PAPER, settings

from . import RectItem


class Paper(RectItem):
    Z = Z_PAPER

    size_name : str

    def __init__(self : 'Paper', size : str):
        super().__init__(QPointF(0, 0), outline=False)
        self.setZValue(Z_PAPER)
        self.setSize(size)

    def setSize(self : 'Paper', size_name : str) -> None:
        self.size_name = size_name
        size = getattr(settings.sheet_sizes, size_name)
        self.setPosSize(QPointF(0, 0), QSizeF(size.width(), size.height()))
