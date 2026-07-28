from __future__ import annotations

from typing import Self
from enum   import StrEnum

from PyQt6.QtCore    import Qt, QPointF
from PyQt6.QtWidgets import QMenu, QGraphicsPathItem, QGraphicsItem
from PyQt6.QtGui     import QAction, QPen

from ....app import settings

from ....core.check import checked

from ..scenes import withScene

from .role import ChromeItem

from .protocols import MoveHandleByProtocol

from .mixin.move      import ItemMoveMixin
from .mixin.scene     import ItemSceneMixin
from .mixin.transform import ItemTransformMixin
from .mixin.change    import ItemChangeMixin
from .mixin.menu      import ItemMenuMixin


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.diagram  import DiagramView
    from ..scenes.diagram import DiagramScene
    from .handle          import HandleItem


class GripShape(StrEnum):
    SQUARE  = "Square"   # origin
    CIRCLE  = "Circle"   # resize/move
    DIAMOND = "Diamond"  # vertex
    ARROW   = "Arrow"    # segment
    STAR    = "Star"     # hotspot


class GripItem(
    ItemSceneMixin,
    ChromeItem,
    ItemMoveMixin,
    ItemChangeMixin,
    ItemMenuMixin,
    QGraphicsPathItem
):
    @checked
    def __init__(
        self   : Self,
        parent : QGraphicsItem,
        pos    : QPointF | None = None,
        move   : bool = False,
        resize : bool = False
    ) -> None:
        super().__init__(parent)
        self.setPos(pos or QPointF(0, 0))
        self.setFlag( self.GraphicsItemFlag.ItemIgnoresTransformations , True  )
        self.setFlag( self.GraphicsItemFlag.ItemIsSelectable           , False )
        self.setFlag( self.GraphicsItemFlag.ItemIsMovable              , False )
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setVisible(False)
        self.onSettingsChanged()
        settings().changed.connect(self.onSettingsChanged)

    @checked
    def onSettingsChanged(self : Self) -> None:
        self.onSceneChanged(self.scene())

    @checked
    def onSceneChanged(self : Self, scene : DiagramScene | None) -> None:
        if scene is None:
            return
        self.setPen(scene.resources.pen("Grip"))
        self.setBrush(scene.resources.brush("Grip"))
        self.updatePath(scene)

    @withScene
    @checked
    def updatePath(self : Self, scene : DiagramScene | None = None) -> None:
        raise NotImplementedError("Subclasses must implement this method")

    @checked
    def moveBy(
        self : Self, dx : float, dy : float) -> None:
        raise NotImplementedError("Subclasses must implement this method")


class HandleGripItem(GripItem):
    @checked
    def __init__(
        self   : Self,
        handle : HandleItem,
        pos    : QPointF | None = None,
        move   : bool = False,
        resize : bool = False
    ) -> None:
        super().__init__(handle)

    @checked
    def handle(self : Self) -> HandleItem | None:
        from .handle import HandleItem
        if isinstance(parent := self.parentItem(), HandleItem | None):
            return parent
        else:
            raise TypeError("Bad parent")

    @checked
    def item(self : Self) -> QGraphicsItem | None:
        if (handle := self.handle()) is None:
            raise TypeError("No handle")
        return handle.parentItem()

    @checked
    def moveBy(self : Self, dx : float, dy : float) -> None:
        if (item := self.item()) is None:
            raise TypeError("No item")
        if isinstance(item, MoveHandleByProtocol):
            if (handle := self.handle()) is None:
                raise TypeError("No handle")
            item.moveHandleBy(handle.id(), QPointF(dx, dy))
        else:
            raise TypeError("Bad item")


class GripShapeMixin:
    _SHAPE : GripShape

    @withScene
    @checked
    def updatePath(self : Self, scene : DiagramScene | None = None) -> None:
        if not isinstance(self, GripItem):
            raise TypeError("Bad host")
        if scene is None:
            raise TypeError("No scene")
        self.setPath(scene.resources.path("Grip", self._SHAPE))


class OriginGripShapeMixin:
    # class attributes
    _NORMAL_SHAPE : GripShape
    _ORIGIN_SHAPE : GripShape

    @withScene
    @checked
    def updatePath(
        self  : Self,
        scene : DiagramScene | None = None
    ) -> None:
        if not isinstance(self, HandleGripItem):
            raise TypeError("Bad host")
        item = self.item()
        normal_shape = getattr(item, "_NORMAL_GRIP_SHAPE", self._NORMAL_SHAPE)
        origin_shape = getattr(item, "_ORIGIN_GRIP_SHAPE", self._ORIGIN_SHAPE)
        if (handle := self.handle()) is None:
            raise TypeError("No handle")
        shape = origin_shape if handle.isOrigin() else normal_shape
        if scene is None:
            raise TypeError("No scene")
        self.setPath(scene.resources.path("Grip", shape))


class MoveGripItem(OriginGripShapeMixin, HandleGripItem):
    """Grip for moving the item."""

    # class attributes
    _NORMAL_SHAPE = GripShape.CIRCLE
    _ORIGIN_SHAPE = GripShape.SQUARE

    @checked
    def ctxMenuItems(
        self : Self,
        view : DiagramView,
        spos : QPointF
    ) -> list[QAction | QMenu]:
        if (item := self.item()) is None:
            raise TypeError("No item")
        entries : list[QAction | QMenu] = [
            view.action(
                "Slide", lambda i = item: view.editSlide([i], self.scenePos())
            ),
            view.action(
                "Move", lambda i = item: view.editMove([i], self.scenePos())
            )
        ]
        item = self.item()
        if isinstance(item, ItemTransformMixin) and item.hasOrigin():
            if (h := self.handle()) is not None:
                entries.extend([
                    view.separator(),
                    view.action(
                        "Assign Origin",
                        lambda: view.editAssignOrigin(item=item, handle=h.id())
                    )
                ])
        return entries


class ResizeGripItem(MoveGripItem):
    """Grip for resizing the item."""

    @checked
    def ctxMenuItems(
        self : Self,
        view : DiagramView,
        spos : QPointF
    ) -> list[QAction | QMenu]:
        entries : list[QAction | QMenu] = [
            view.action("Resize", lambda: view.editResize(self, self.scenePos())),
        ]
        entries.extend(super().ctxMenuItems(view, spos))
        return entries
