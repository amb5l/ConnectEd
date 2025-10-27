from typing import Self

from PyQt6.QtCore    import Qt, QPointF, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsItem
from PyQt6.QtGui     import QPen, QBrush, QPainterPath

from ....app import settings

from .mixin.change import ItemChangeMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.drawing import DrawingScene
    from .mixin.anchor    import ItemAnchorPointsMixin


class Handle(
    ItemChangeMixin,
    QGraphicsPathItem
):
    # class attributes
    _PATH_NAME = "Handle"

    # instance attributes
    _item      : "ItemAnchorPointsMixin"  # parent item
    _path_name : str                      # path name
    _xxxpath      : QPainterPath             # path
    _brush     : QBrush                   # brush

    def __init__(
        self   : Self,
        parent : QGraphicsItem,
        pos    : QPointF | None = None,
        move   : bool = False,
        resize : bool = False
    ) -> None:
        super().__init__(parent)
        if pos is None:
            pos = QPointF()
        self.setPos(pos)
        self._item = parent.parentItem()
        self.setFlag( self.GraphicsItemFlag.ItemIgnoresTransformations , True  )
        self.setFlag( self.GraphicsItemFlag.ItemIsSelectable           , False )
        self.setFlag( self.GraphicsItemFlag.ItemIsMovable              , False )
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self._brush = QBrush(Qt.BrushStyle.SolidPattern)
        self.setVisible(False)
        self._path_name = self._PATH_NAME
        self.onSettingsChange()
        settings().changed.connect(self.onSettingsChange)

    def onSceneChange(self : Self, scene : "DrawingScene | None") -> None:
        if scene is not None:
            self.setPath(scene.paths[self._path_name])

    def onSettingsChange(self : Self) -> None:
        self.prepareGeometryChange()
        self.onSceneChange(self.scene())
        self._brush.setColor(settings().get("theme/selected/fill"))
        self.setBrush(self._brush)

    def toXml(self : Self, _ : QXmlStreamWriter) -> None:
        pass

    @classmethod
    def fromXml(cls : Self, _ : QXmlStreamReader) -> Self:
        pass
