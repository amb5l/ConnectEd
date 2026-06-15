from PyQt6.QtWidgets import QGraphicsEllipseItem

from .role import DecorativeItem

from .base_rect import BaseRectangleMixin


class EllipseItem(DecorativeItem, BaseRectangleMixin, QGraphicsEllipseItem):
    pass


class SymbolEllipseItem(EllipseItem):
    pass
