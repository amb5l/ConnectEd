import uuid

from typing import Self

from PyQt6.QtCore    import QPointF, QRectF, QSizeF
from PyQt6.QtWidgets import QGraphicsScene
from PyQt6.QtGui     import QUndoStack, QColor

from .....app import settings

from .....core.check import checked
from .....core.types import DataKind
from .....core.doc   import Doc

from ...properties import InherentProperty, PropertiesMixin

from .api       import DrawingSceneApiMixin
from .grips     import DrawingSceneGripsMixin
from .resources import DrawingSceneResources
from .guides    import DrawingSceneGuidesMixin
from .private   import DrawingSceneApiPrivateMixin


class DrawingScene(
    DrawingSceneApiMixin,
    DrawingSceneGripsMixin,
    DrawingSceneGuidesMixin,
    DrawingSceneApiPrivateMixin,
    PropertiesMixin,
    QGraphicsScene
):
    # class attributes
    _RESOURCES_CLS = DrawingSceneResources
    _PROPERTIES = {
        "Name" : InherentProperty["DrawingScene"](
            kind   = DataKind.STR,
            getter = lambda self: self.name(),
            setter = lambda self, value: self.setName(value)
        )
    }

    # instance attributes
    _uuid      : str
    _name      : str
    resources  : DrawingSceneResources
    undo_stack : QUndoStack | None
    _doc       : Doc | None

    @checked
    def __init__(
        self    : Self,
        doc     : Doc | None = None,
        extents : QSizeF | None = None,
        fresh   : bool = True
    ) -> None:
        super().__init__()
        self._uuid = str(uuid.uuid4())
        self._name = "Untitled"
        self.updateSceneRect(extents)
        self.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex)
        self.resources = self._RESOURCES_CLS()
        self.undo_stack = QUndoStack(self)
        self._doc = doc
        self.initProperties(fresh)
        self.initGrips()
        self.selectionChanged.connect(self.onSelectionChanged)
        self.setLive(fresh)

    def __hash__(self : Self):
        return hash(self._uuid)

    def __eq__(self : Self, other):
        if not isinstance(other, DrawingScene):
            return NotImplemented
        return self._uuid == other._uuid

    def onSelectionChanged(self : Self) -> None:
        self.updateGrips()

    def name(self : Self) -> str:
        return self._name

    @checked
    def setName(self : Self, name : str, notify : bool = True) -> None:
        self._name = name
        self.properties.signalChanges("Name")
        if notify and self._doc is not None and self.live():
            self._doc.onChanged()

    def undo(self : Self) -> None:
        self.undo_stack.undo()

    def redo(self : Self) -> None:
        self.undo_stack.redo()

    def updateSceneRect(
        self         : Self,
        rect_or_size : QRectF | QSizeF | None = None
    ) -> None:
        if rect_or_size is None:
            rect = None
        elif isinstance(rect_or_size, QRectF):
            rect = rect_or_size
        else:
            rect = QRectF(QPointF(0, 0), rect_or_size)
        ext_rect = QRectF(QPointF(0, 0), settings().get("defaults/extents"))
        scene_rect = QRectF(rect) if rect is not None else ext_rect
        for item in self.items():
            item_rect = item.mapToScene(item.boundingRect()).boundingRect()
            scene_rect = item_rect if scene_rect is None \
                else scene_rect.united(item_rect)
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
