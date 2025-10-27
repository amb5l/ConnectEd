from typing import Self

from PyQt6.QtWidgets import QStyleOptionGraphicsItem, QWidget, QStyle
from PyQt6.QtGui     import QPainter

class ItemPaintMixin:
    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, option, widget)
