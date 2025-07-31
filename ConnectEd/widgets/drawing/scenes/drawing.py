__all__ = ["DrawingScene"]

from typing import Self, Optional

from PyQt6.QtCore    import pyqtSignal, QPointF, QRectF, QSizeF, \
                            QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsScene
from PyQt6.QtGui     import QUndoStack

from ....core import logger, toXmlAttrs, fromXmlAttrs

from ..items.text_block    import TextBlock

from .api import *

from .... import hub

from ..properties import PropertySpec, PropertiesMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....core import DrawingItem

class DrawingScene(
    DrawingSceneApiMixin,
    PropertiesMixin,
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

    # instance variables
    item       : Optional["DrawingItem"]
    undo_stack : Optional[QUndoStack]

    # custom signals
    textEditingComplete = pyqtSignal(TextBlock)

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

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement(self.__class__.__name__)
        toXmlAttrs(self, xw)
        for item in self.items():
            item.toXml(xw)
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader, parent : Optional["DrawingItem"] = None) -> Self:
        from ..items import element_class_dict
        cls_name = cls.__name__
        if xr.name() != cls_name:
            raise ValueError(f"Expected {cls_name} element, got {xr.name()}")
        drawing_scene : DrawingScene = cls(parent)
        fromXmlAttrs(drawing_scene, xr)
        while not (xr.isEndElement() and xr.name() == cls_name):
            if xr.tokenType() == QXmlStreamReader.TokenType.StartElement:
                attr_name = xr.name()
                if attr_name in element_class_dict:
                    cls = element_class_dict[attr_name]
                    element = cls.fromXml(xr)
                    drawing_scene.addItem(element)
                else:
                    logger.warning(f"Unexpected element: {attr_name}")
            xr.readNext()
        return drawing_scene

    def onTextEditingComplete(self, text_item: TextBlock):
        self.textEditingComplete.emit(text_item)

    def getName(self : Self) -> str:
        return self.item.text()
