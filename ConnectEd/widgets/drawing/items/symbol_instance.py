__all__ = ["SymbolInstance"]

from PyQt6.QtCore    import QRectF
from PyQt6.QtWidgets import QGraphicsItem


class SymbolInstance(QGraphicsItem):
    _fence : QRectF  # boundary; parent for pins
