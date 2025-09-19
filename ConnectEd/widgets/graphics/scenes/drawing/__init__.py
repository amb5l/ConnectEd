from typing import Self, Optional

from PyQt6.QtCore    import QPointF, QRectF, QSizeF, \
                            QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsScene
from PyQt6.QtGui     import QUndoStack

from .....app import logger, settings

from .....core.xml import toXmlAttrs, fromXmlAttrs

from ...properties import PropertySpec, PropertiesMixin

from .file    import DrawingSceneApiFileMixin
from .edit    import DrawingSceneApiEditMixin
from .private import DrawingSceneApiPrivateMixin
from .paths   import DrawingScenePathsMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .....core.db import DrawingItem

class DrawingScene(
    PropertiesMixin,
    DrawingSceneApiFileMixin,
    DrawingSceneApiEditMixin,
    DrawingSceneApiPrivateMixin,
    DrawingScenePathsMixin,
    QGraphicsScene
):
    # class attributes
    _PROPERTY_SPECS = {
        "Name" : PropertySpec(
            type_name = "str",
            getter    = lambda self: self._name,
            setter    = lambda self, value: setattr(self, '_name', value)
        )
    }

    # instance attributes
    item       : Optional["DrawingItem"]
    undo_stack : Optional[QUndoStack]
    _name      : str

    def __init__(
        self    : Self,
        item    : "DrawingItem",
        extents : Optional[QSizeF] = None
    ) -> None:
        super().__init__()
        self.item = item
        self._name = ""
        self.updateSceneRect()
        self.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex)
        self.undo_stack = None
        self.undo_stack = QUndoStack(self)
        self.initProperties()
        self.initPaths()

    def setParent(self : Self, parent : "DrawingItem") -> None:
        self.item = parent

    @property
    def name(self : Self) -> str:
        return self._name

    @name.setter
    def name(self : Self, name : str) -> None:
        self._name = name

    def undo(self : Self) -> None:
        self.undo_stack.undo()

    def redo(self : Self) -> None:
        self.undo_stack.redo()

    def updateSceneRect(self : Self, rect : Optional[QRectF] = None) -> None:
        ext_rect = QRectF(QPointF(0, 0), settings().get("defaults/extents"))
        scene_rect = rect or ext_rect
        for item in self.items():
            item_rect = item.mapToScene(item.boundingRect()).boundingRect()
            scene_rect = item_rect if scene_rect is None else scene_rect.united(item_rect)
        if scene_rect is not None:
            self.setSceneRect(scene_rect)

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement(self.__class__.__name__.replace("Scene", ""))
        toXmlAttrs(self, xw)
        for item in self.items():
            item.toXml(xw)
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader, parent : Optional["DrawingItem"] = None) -> Self:
        from ...items import _element_classes
        cls_name = cls.__name__
        # Use the same naming convention as toXml: remove "Scene" suffix
        expected_element_name = cls_name.replace("Scene", "")
        if xr.name() != expected_element_name:
            raise ValueError(f"Expected {expected_element_name} element, got {xr.name()}")
        drawing_scene : DrawingScene = cls(parent)
        fromXmlAttrs(drawing_scene, xr)
        while not (xr.isEndElement() and xr.name() == expected_element_name):
            if xr.tokenType() == QXmlStreamReader.TokenType.StartElement:
                attr_name = xr.name()
                if attr_name in _element_classes:
                    element_cls = _element_classes[attr_name]
                    element = element_cls.fromXml(xr)
                    drawing_scene.addItem(element)
                else:
                    logger().warning(f"Unexpected element: {attr_name}")
            xr.readNext()
        return drawing_scene
