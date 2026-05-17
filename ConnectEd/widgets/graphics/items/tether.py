from typing import Self

from PyQt6.QtCore    import QPointF, QXmlStreamWriter
from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsItem, \
                            QGraphicsSceneMouseEvent

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.drawing import DrawingScene
    from .text            import TextItem


class TextTetherItem(QGraphicsLineItem):
    """
    Tether line from the origin of a text item to its parent (handle/node).
    """

    _text_item  : "TextItem"  # text item instance

    def __init__(self : Self, text_item : "TextItem"):
        self._text_item = text_item
        super().__init__(text_item.getOriginHandle())
        self.setVisible(text_item.isSelected())
        self.onSettingsChanged()
        self.onPositionChanged(self._text_item.pos())

    def mousePressEvent(self : Self, event : QGraphicsSceneMouseEvent) -> None:
        self._text_item.mousePressEvent(event)

    def mouseReleaseEvent(self : Self, event : QGraphicsSceneMouseEvent) -> None:
        self._text_item.mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self : Self, event : QGraphicsSceneMouseEvent) -> None:
        self._text_item.mouseDoubleClickEvent(event)

    def onSettingsChanged(self : Self) -> None:
        if scene := self.scene() is not None:
            self.onSceneChanged(scene)

    def onSceneChanged(self : Self, scene : "DrawingScene | None") -> None:
        if scene is None:
            return
        self.setPen(scene.resources.pen("Tether"))

    def onPositionChanged(self : Self, _ : QPointF | None = None) -> None:
        if self.anchor() is None:
            return
        line = self.line()
        line.setP2(self.mapFromItem(self.anchor(), QPointF(0, 0)))
        self.setLine(line)

    def anchor(self : Self) -> QGraphicsItem | None:
        return self._text_item.parentItem()

    def toXml(self : Self, _xw : QXmlStreamWriter) -> str:
        pass  # no need to serialise
