import uuid

from typing import Self

from PyQt6.QtCore    import QPointF, QRectF, QSizeF, \
                            QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsScene
from PyQt6.QtGui     import QUndoStack

from .....app import logger, settings

from .....core.xml import toXmlAttrs, fromXmlAttrs

from ...properties import PropertySpec, PropertiesMixin

from .edit    import DrawingSceneApiEditMixin
from .private import DrawingSceneApiPrivateMixin
from .paths   import DrawingScenePathsMixin
from .handles import DrawingSceneHandlesMixin
from .conn    import DrawingSceneConnMixin


class DrawingScene(
    PropertiesMixin,
    DrawingSceneApiEditMixin,
    DrawingSceneApiPrivateMixin,
    DrawingScenePathsMixin,
    DrawingSceneHandlesMixin,
    DrawingSceneConnMixin,
    QGraphicsScene
):
    # class attributes
    _PROPERTY_SPECS = {
        "Name" : PropertySpec(
            type_name = "str",
            getter    = lambda self: self._name,
            setter    = lambda self, value : setattr(self, '_name', value)
        )
    }

    # instance attributes
    _uuid      : str
    _name      : str | None
    undo_stack : QUndoStack | None

    def __init__(self : Self, extents : QSizeF | None = None) -> None:
        super().__init__()
        self._uuid = str(uuid.uuid4())
        self._name = None
        self.updateSceneRect(extents)
        self.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex)
        self.undo_stack = QUndoStack(self)
        self.initProperties()
        self.initPaths()
        self.initHandle()
        self.selectionChanged.connect(self.onSelectionChanged)

    def __hash__(self : Self):
        return hash(self._uuid)

    def __eq__(self : Self, other):
        if not isinstance(other, DrawingScene):
            return NotImplemented
        return self._uuid == other._uuid

    def onSelectionChanged(self : Self) -> None:
        self.updateHandles()

    def name(self : Self) -> str | None:
        return self._name

    def setName(self : Self, name : str | None) -> None:
        self._name = name

    def undo(self : Self) -> None:
        self.undo_stack.undo()

    def redo(self : Self) -> None:
        self.undo_stack.redo()

    def updateSceneRect(self : Self, rect : QRectF | None = None) -> None:
        ext_rect = QRectF(QPointF(0, 0), settings().get("defaults/extents"))
        scene_rect = QRectF(rect) if rect is not None else ext_rect
        for item in self.items():
            item_rect = item.mapToScene(item.boundingRect()).boundingRect()
            scene_rect = item_rect if scene_rect is None else scene_rect.united(item_rect)
        if scene_rect is not None:
            # triple size of calculated scene rect
            w = scene_rect.size().width()
            h = scene_rect.size().height()
            scene_rect.setRect(
                scene_rect.left() - w,
                scene_rect.top() - h,
                w * 3,
                h * 3
            )
            self.setSceneRect(scene_rect)

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement(self.__class__.__name__.replace("Scene", ""))
        toXmlAttrs(self, xw)
        for item in self.items():
            if item.parentItem() is None:  # top level items only
                item.toXml(xw)
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        from ...items import _item_classes
        cls_name = cls.__name__
        # Use the same naming convention as toXml: remove "Scene" suffix
        expected_element_name = cls_name.replace("Scene", "")
        if xr.name() != expected_element_name:
            raise ValueError(f"Expected {expected_element_name} element, got {xr.name()}")
        drawing_scene : DrawingScene = cls()
        fromXmlAttrs(drawing_scene, xr)
        while not (xr.isEndElement() and xr.name() == expected_element_name):
            if xr.tokenType() == QXmlStreamReader.TokenType.StartElement:
                attr_name = xr.name()
                if attr_name in _item_classes:
                    item_cls = _item_classes[attr_name]
                    item = item_cls.fromXml(xr)
                    drawing_scene.addItem(item)
                else:
                    logger().warning(f"Unexpected element: {attr_name}")
            xr.readNext()
        drawing_scene.tidyConns(undo=False)
        return drawing_scene
