from typing import Self

from PyQt6.QtGui     import QPainter
from PyQt6.QtWidgets import QGraphicsItem, \
                            QStyleOptionGraphicsItem, QWidget, QStyle

from .....core.check import checked
from .....core.utils import qtItemClass

from ..protocols import SetPenProtocol, SetBrushProtocol, SetQuillProtocol


class ItemSelectMixin:
    # class attributes
    _SELECT_MODES = 1

    # instance attributes
    _select_mode : int = 0

    def initSelect(self : Self) -> None:
        from .presentation import ItemPresentationMixin
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
        self : Self,
        selected : bool
    ) -> None:
        if not isinstance(self, QGraphicsItem): raise TypeError("Bad host")
        from ...scenes.diagram import DiagramScene
        from .presentation import ItemPresentationMixin
        self.setSelectMode(0)
        # update pen/brush/text from scene resources
        if  isinstance(scene := self.scene(), DiagramScene) \
        and isinstance(self, ItemPresentationMixin):
            if isinstance(self, SetPenProtocol):
                self._updatePen(scene)
            if isinstance(self, SetBrushProtocol):
                self._updateBrush(scene)
            if isinstance(self, SetQuillProtocol):
                self._updateQuill(scene)

    def paint(
        self    : Self,
        painter : QPainter | None,
        option  : QStyleOptionGraphicsItem | None,
        widget  : QWidget | None = None
    ) -> None:
        """Suppress Qt's built-in selected appearance."""
        if not isinstance(self, QGraphicsItem): raise TypeError("Bad host")
        if isinstance(option, QStyleOptionGraphicsItem):
            option.state &= ~QStyle.StateFlag.State_Selected
        qtItemClass(self).paint(self, painter, option, widget)
