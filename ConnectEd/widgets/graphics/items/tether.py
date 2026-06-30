from __future__ import annotations

from typing import Self

from PyQt6.QtCore    import QPointF

from ....core.check import checked
from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsItem, \
                            QGraphicsSceneMouseEvent

from .role import ChromeItem

from .mixin.settings import ItemSettingsMixin
from .mixin.change   import ItemChangeMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.diagram import DiagramScene
    from .text            import TextItem


class TextTetherItem(
    ChromeItem,
    ItemChangeMixin,
    ItemSettingsMixin,
    QGraphicsLineItem
):
    """
    Tether line from the origin of a text item to its parent (handle/node).
    """

    _text_item  : TextItem  # text item instance

    @checked
    def __init__(self : Self, text_item : TextItem) -> None:
        self._text_item = text_item
        self.initSettings()
        self.initChange()
        super().__init__(text_item.getOriginHandle())
        self.setVisible(text_item.isSelected())
        self.onSettingsChanged()
        self.onPositionChanged(self._text_item.pos())

    def mousePressEvent(
        self  : Self,
        event : QGraphicsSceneMouseEvent | None
    ) -> None:
        self._text_item.mousePressEvent(event)

    def mouseReleaseEvent(
        self  : Self,
        event : QGraphicsSceneMouseEvent | None
    ) -> None:
        self._text_item.mouseReleaseEvent(event)

    def mouseDoubleClickEvent(
        self  : Self,
        event : QGraphicsSceneMouseEvent | None
    ) -> None:
        self._text_item.mouseDoubleClickEvent(event)

    def onSettingsChanged(self : Self) -> None:
        from ..scenes.diagram import DiagramScene
        if isinstance(scene := self.scene(), DiagramScene):
            self.onSceneChanged(scene)

    @checked
    def onSceneChanged(self : Self, scene : DiagramScene | None) -> None:
        if scene is None:
            return
        self.setPen(scene.resources.pen("Tether"))

    @checked
    def onPositionChanged(self : Self, _ : QPointF | None = None) -> None:
        if self.anchor() is None:
            return
        line = self.line()
        line.setP2(self.mapFromItem(self.anchor(), QPointF(0, 0)))
        self.setLine(line)

    def anchor(self : Self) -> QGraphicsItem | None:
        return self._text_item.parentItem()
