from typing import Self, Optional

from PyQt6.QtCore    import pyqtSignal, QPointF, QRectF, QSizeF, \
                            QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsScene
from PyQt6.QtGui     import QUndoStack

from .... import hub

from ....core.log import logger
from ....core.xml import toXmlAttrs, fromXmlAttrs

from ..items.text_block import TextBlock

from ..properties import PropertySpec, PropertiesMixin

from .api.file    import DrawingSceneApiFileMixin
from .api.edit    import DrawingSceneApiEditMixin
from .api.private import DrawingSceneApiPrivateMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....core import DrawingItem

class DrawingScene(
    PropertiesMixin,
    DrawingSceneApiFileMixin,
    DrawingSceneApiEditMixin,
    DrawingSceneApiPrivateMixin,
    QGraphicsScene
):
    # class variables
    _PROPERTY_SPECS = {
        "Name" : PropertySpec(
            type_name = "str",
            getter    = lambda self: self.getName(),
            setter    = lambda self, value: self.setName(value)
        )
    }

    # instance attributes
    item       : Optional["DrawingItem"]
    undo_stack : Optional[QUndoStack]

    def __init__(
        self    : Self,
        item    : "DrawingItem",
        extents : Optional[QSizeF] = None
    ) -> None:
        super().__init__()
        self.item = item
        if extents is None:
            extents = hub.settings.get("defaults/extents")
        self.setSceneRect(QRectF(QPointF(0, 0), extents))
        self.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex)
        self.undo_stack = None
        self.undo_stack = QUndoStack(self)
        self.initProperties()

    def setParent(self : Self, parent : "DrawingItem") -> None:
        self.item = parent

    def undo(self : Self) -> None:
        self.undo_stack.undo()

    def redo(self : Self) -> None:
        self.undo_stack.redo()

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement(self.__class__.__name__)
        toXmlAttrs(self, xw)
        for item in self.items():
            item.toXml(xw)
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader, parent : Optional["DrawingItem"] = None) -> Self:
        from ..items import _element_classes
        cls_name = cls.__name__
        if xr.name() != cls_name:
            raise ValueError(f"Expected {cls_name} element, got {xr.name()}")
        drawing_scene : DrawingScene = cls(parent)
        fromXmlAttrs(drawing_scene, xr)
        while not (xr.isEndElement() and xr.name() == cls_name):
            if xr.tokenType() == QXmlStreamReader.TokenType.StartElement:
                attr_name = xr.name()
                if attr_name in _element_classes:
                    cls = _element_classes[attr_name]
                    element = cls.fromXml(xr)
                    drawing_scene.addItem(element)
                else:
                    logger.warning(f"Unexpected element: {attr_name}")
            xr.readNext()
        return drawing_scene
