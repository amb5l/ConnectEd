import uuid

from typing import Self

from PyQt6.QtCore    import QPointF, QRectF, QSizeF, \
                            QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsScene
from PyQt6.QtGui     import QUndoStack, QColor

from .....app import logger, settings

from .....core.xml import toXmlAttrs, fromXmlAttrs

from ...properties import InherentProperty, PropertiesMixin

from .api        import DrawingSceneApiMixin
from .grips      import DrawingSceneGripsMixin
from .paths      import DrawingScenePathsMixin
from .guides     import DrawingSceneGuidesMixin
from .netlist    import DrawingSceneNetlistMixin
from .private    import DrawingSceneApiPrivateMixin


class DrawingScene(
    DrawingSceneApiMixin,
    DrawingSceneGripsMixin,
    DrawingScenePathsMixin,
    DrawingSceneGuidesMixin,
    DrawingSceneNetlistMixin,
    DrawingSceneApiPrivateMixin,
    PropertiesMixin,
    QGraphicsScene
):
    # class attributes
    _PROPERTIES = {
        "Name" : InherentProperty(
            kind   = "str",
            getter = lambda self: self._name,
            setter = lambda self, value : setattr(self, "_name", value)
        )
    }

    # instance attributes
    _uuid      : str
    _name      : str | None
    _sel_line  : QColor
    _sel_fill  : QColor
    _sel_text  : QColor
    undo_stack : QUndoStack | None

    def __init__(self : Self, extents : QSizeF | None = None, fresh : bool = True) -> None:
        super().__init__()
        self._uuid = str(uuid.uuid4())
        self._name = None
        self.updateSceneRect(extents)
        self.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex)
        self.undo_stack = QUndoStack(self)
        self.initProperties(fresh)
        self.initPaths()
        self.initGrips()
        self.onSettingsChange()
        settings().changed.connect(self.onSettingsChange)
        self.selectionChanged.connect(self.onSelectionChanged)

    def __hash__(self : Self):
        return hash(self._uuid)

    def __eq__(self : Self, other):
        if not isinstance(other, DrawingScene):
            return NotImplemented
        return self._uuid == other._uuid

    def onSettingsChange(self : Self) -> None:
        self._sel_line = settings().get("theme/selected/line")
        self._sel_fill = settings().get("theme/selected/fill")
        self._sel_text = settings().get("theme/selected/text")

    def onSelectionChanged(self : Self) -> None:
        self.updateGrips()

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

    def selectedLineColor(self : Self) -> QColor:
        return self._sel_line

    def selectedFillColor(self : Self) -> QColor:
        return self._sel_fill

    def selectedTextColor(self : Self) -> QColor:
        return self._sel_text

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
        top_element_name = cls.__name__.replace("Scene", "")
        if xr.name() != top_element_name:
            raise ValueError(f"Expected {top_element_name} element, got {xr.name()}")
        drawing_scene : DrawingScene = cls()
        fromXmlAttrs(drawing_scene, xr)
        while not (xr.isEndElement() and xr.name() == top_element_name):
            if xr.tokenType() == QXmlStreamReader.TokenType.StartElement:
                attr_name = xr.name()
                if attr_name in _item_classes:
                    item_cls = _item_classes[attr_name]
                    item = item_cls.fromXml(xr)
                    drawing_scene.addItem(item)
                else:
                    logger().warning(f"Unexpected element: {attr_name}")
            xr.readNext()
        drawing_scene.tidyConns(undoable=False)
        return drawing_scene
