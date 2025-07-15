__all__ = ["DrawingScene"]

from typing import Self, Optional

from PyQt6.QtCore    import pyqtSignal, QPointF, QRectF, QSizeF, \
                            QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsItem
from PyQt6.QtGui     import QUndoStack

from ....core import logger, toXmlAttrs, fromXmlAttrs

from ..items import PropertiesMixin, ElementMixin, element_class_dict

from ..items.text_block    import TextBlock
from ..items.property_text import PropertyText

from .api import *

from .... import hub

from .. import AttrSpec

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....core import DrawingItem


class DrawingScene(
    QGraphicsScene,
    DrawingSceneApiMixin,
    PropertiesMixin
):
    # class variables
    _ATTR_SPECS = [
        AttrSpec(
            name      = "Name",
            type_name = "str",
            exists    = lambda self: True,
            getter    = lambda self: self.getName(),
            setter    = lambda self, value: self.setName(value)
        )
    ]

    # instance variables
    item       : Optional["DrawingItem"]
    undo_stack : Optional[QUndoStack]
    kp_items   : list[QGraphicsItem] # TODO private name

    # custom signals
    selectionChangedItems = pyqtSignal("QList<QGraphicsItem*>")
    textEditingComplete   = pyqtSignal(TextBlock)

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
        self.kp_items = []
        self.undo_stack = QUndoStack(self)
        if hub.main_window: # GUI is running
            self.selectionChanged.connect(self.onSelectionChanged)
        self.initProperties()

    def setParent(self : Self, parent : "DrawingItem") -> None:
        self.item = parent

    def clearSelection(self : Self) -> None:
        super().clearSelection()
        for item in self.items():
            if isinstance(item, ElementMixin):
                item.setKPVisible(False)
        self.kp_items.clear()

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement(self.__class__.__name__)
        toXmlAttrs(self, xw)
        for item in self.items():
            item.toXml(xw)
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader, parent : Optional["DrawingItem"] = None) -> Self:
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

    def onSelectionChanged(self : Self) -> None:
        # Hide key points for previously selected items
        if self.kp_items:
            for kp_item in self.kp_items:
                if kp_item.scene() == self:  # Ensure item still exists
                    kp_item.setKPVisible(False)
            self.kp_items.clear()
        # Show key points only if exactly one item is selected
        items = self.selectedItems()
        if len(items) == 1:
            items[0].setKPVisible(True)
            self.kp_items.append(items[0])
        self.selectionChangedItems.emit(items)

    def onTextEditingComplete(self, text_item: TextBlock):
        self.textEditingComplete.emit(text_item)

    def getName(self : Self) -> str:
        return self.item.text()
