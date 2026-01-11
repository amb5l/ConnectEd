from typing import Self, overload

from PyQt6.QtWidgets import QGraphicsItem, QGraphicsSimpleTextItem, \
                            QGraphicsSceneContextMenuEvent
from PyQt6.QtGui     import QColor

from ..mixin.rotate import ItemRotateMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import UniText


class UniTextLine(QGraphicsSimpleTextItem):
    @overload
    def __init__(self, parent: QGraphicsItem | None = None) -> None:
        ...

    @overload
    def __init__(self, text: str, parent: QGraphicsItem | None = None) -> None:
        ...

    def __init__(
        self           : Self,
        text_or_parent : str | QGraphicsItem | None = None,
        parent         : QGraphicsItem | None = None
    ) -> None:
        if isinstance(text_or_parent, str):
            super().__init__(text_or_parent, parent)
        else:
            super().__init__(parent=parent)

    def onSceneRotationChange(self : Self) -> None:
        """Rotation compensation."""
        a = ItemRotateMixin.sceneRotation(self)
        self.setRotation(180 if a > 135 and a <= 315 else 0)

    def color(self : Self) -> QColor:
        return self.brush().color()

    def setColor(self : Self, color : QColor) -> None:
        brush = self.brush()
        brush.setColor(color)
        self.setBrush(brush)

    def contextMenuEvent(
        self  : Self,
        event : QGraphicsSceneContextMenuEvent
    ) -> None:
        """Bounce context menu event to parent."""
        parent: "UniText" = self.parentItem()
        if parent is not None:
            parent.contextMenuEvent(event)
        else:
            super().contextMenuEvent(event)
