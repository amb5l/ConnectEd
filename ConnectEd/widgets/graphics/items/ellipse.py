from PyQt6.QtWidgets import QGraphicsEllipseItem

from .base_rect import BaseRectangleMixin


class EllipseItem(BaseRectangleMixin, QGraphicsEllipseItem):
    pass


class SymbolEllipseItem(EllipseItem):
    pass
