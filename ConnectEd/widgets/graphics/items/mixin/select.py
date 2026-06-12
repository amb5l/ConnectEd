from typing import Self

from PyQt6.QtGui     import QPainter
from PyQt6.QtWidgets import QStyleOptionGraphicsItem, QWidget, QStyle

from .....core.check import checked

from .presentation import ItemPresentationMixin


class ItemSelectMixin:
    # class attributes
    _SELECT_MODES = 1

    # instance attributes
    _select_mode : int = 0

    def initSelect(self : Self) -> None:
        if not isinstance(self, ItemPresentationMixin):
            raise TypeError("This item does not support the ItemPresentationMixin")

    @checked
    def selectMode(self : Self) -> int:
        return self._select_mode

    @checked
    def setSelectMode(self : Self, mode : int) -> None:
        if self._select_mode == mode:
            return
        self._select_mode = mode
        self.onSelectionModeChanged()

    @checked
    def cycleSelectMode(self : Self) -> None:
        self.setSelectMode((self._select_mode + 1) % self._SELECT_MODES)

    def onSelectionModeChanged(self : Self) -> None:
        """Post-hook when selection edit mode changes."""
        pass

    @checked
    def onSelectionChanged(
        self : Self | ItemPresentationMixin,
        selected : bool
    ) -> None:
        self.setSelectMode(0)
        # update pen/brush/text from scene resources
        if hasattr(self, "setPen"):
            self._updatePen(self.scene())
        if hasattr(self, "setBrush"):
            self._updateBrush(self.scene())
        if hasattr(self, "setQuill"):
            self._updateQuill(self.scene())

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        """Suppress Qt's built-in selected appearance."""
        option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, option, widget)
