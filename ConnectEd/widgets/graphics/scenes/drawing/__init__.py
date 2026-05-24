import uuid

from typing import Self

from PyQt6.QtCore    import QPointF, QRectF, QSizeF
from PyQt6.QtWidgets import QGraphicsScene
from PyQt6.QtGui     import QUndoStack, QColor

from .....app import settings

from .....core.types import DataKind

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
        "Name" : InherentProperty(
            kind   = DataKind.STR,
            getter = lambda self: self.name(),
            setter = lambda self, value: self.setName(value)
        )
    }

    # instance attributes
    _uuid      : str
    _name      : str | None
    _sel_line  : QColor  # TODO delete
    _sel_fill  : QColor
    _sel_text  : QColor
    resources  : DrawingSceneResources
    undo_stack : QUndoStack | None

    def __init__(
        self    : Self,
        extents : QSizeF | None = None,
        fresh   : bool = True
    ) -> None:
        super().__init__()
        self._uuid = str(uuid.uuid4())
        self._name = None
        self.updateSceneRect(extents)
        self.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex)
        self.undo_stack = QUndoStack(self)
        self.resources = self._RESOURCES_CLS()
        self.initProperties(fresh)
        self.initGrips()
        self.onSettingsChanged()
        settings().changed.connect(self.onSettingsChanged)
        self.selectionChanged.connect(self.onSelectionChanged)
        self.properties.setNotify(fresh)

    def __hash__(self : Self):
        return hash(self._uuid)

    def __eq__(self : Self, other):
        if not isinstance(other, DrawingScene):
            return NotImplemented
        return self._uuid == other._uuid

    def onSettingsChanged(self : Self) -> None:
        self._sel_line = settings().get("theme/selected/line")
        self._sel_fill = settings().get("theme/selected/fill")
        self._sel_text = settings().get("theme/selected/text")

    def onSelectionChanged(self : Self) -> None:
        self.updateGrips()

    def name(self : Self) -> str | None:
        return self._name

    def setName(self : Self, name : str | None) -> None:
        self._name = name
        self.properties.signalChanges("Name")

    def undo(self : Self) -> None:
        self.undo_stack.undo()

    def redo(self : Self) -> None:
        self.undo_stack.redo()

    def updateSceneRect(self : Self, rect : QRectF | None = None) -> None:
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

    def selectedLineColor(self : Self) -> QColor:
        return self._sel_line

    def selectedFillColor(self : Self) -> QColor:
        return self._sel_fill

    def selectedTextColor(self : Self) -> QColor:
        return self._sel_text
