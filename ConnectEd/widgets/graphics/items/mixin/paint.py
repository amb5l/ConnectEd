from typing import Self

from PyQt6.QtWidgets import QGraphicsItem, \
                            QStyleOptionGraphicsItem, QWidget, QStyle
from PyQt6.QtGui     import QPainter

from .....core.utils import qtItemClass


class ItemPaintMixin:
    def paint(
        self    : Self,
        painter : QPainter | None = None,
        option  : QStyleOptionGraphicsItem | None = None,
        widget  : QWidget | None = None
    ) -> None:
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        if option is not None:
            option.state &= ~QStyle.StateFlag.State_Selected
        qtItemClass(self).paint(self, painter, option, widget)
