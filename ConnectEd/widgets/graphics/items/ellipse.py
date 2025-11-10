from PyQt6.QtWidgets import QGraphicsEllipseItem

from .base_rect import BaseRectangleMixin


class Ellipse(BaseRectangleMixin, QGraphicsEllipseItem):
    pass


class SymbolEllipse(Ellipse):
    pass
