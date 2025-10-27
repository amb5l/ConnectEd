from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui     import QAction

from .handle import Handle

from .mixin.origin import ItemOriginMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing import DrawingView
    from ..scenes.drawing import DrawingScene
    from .anchor_point import AnchorPoint


class Grip(Handle):
    """Grip for anchor points."""

    _PATH_NAME = "Grip"

    def __init__(
        self   : Self,
        parent : "AnchorPoint",
        pos    : QPointF | None = None,
        move   : bool = False,
        resize : bool = False
    ) -> None:
        super().__init__(parent, pos, move, resize)
        self.onOriginChange()

    def onOriginChange(self : Self) -> None:
        ap : "AnchorPoint" = self.parentItem()
        item = ap.parentItem()
        if not isinstance(item, ItemOriginMixin):
            return
        if item.getOriginAPName() == ap.name():
            self._path_name = "Origin"
        else:
            self._path_name = self._PATH_NAME
        scene : "DrawingScene" = self.scene()
        if scene:
            self.setPath(scene.paths[self._path_name])

    def moveBy(self : Self, delta : QPointF) -> None:
        parent : "AnchorPoint" = self.parentItem()
        self._item.moveAnchorPointBy(parent.name(), delta)


class MoveGrip(Grip):
    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        items = [
            view.action("Slide", view.ui.editSlide),
            view.action("Move", view.ui.editMove)
        ]
        if isinstance(self._item, ItemOriginMixin):
            items.extend([
                view.separator(),
                view.action(
                    "Assign Origin",
                    lambda: view.ui.editAssignOrigin(self.parentItem())
                )
            ])
        return items


class ResizeGrip(MoveGrip):
    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        items = [
            view.action("Resize", lambda: view.ui.editResize(self)),
        ]
        if isinstance(self._item, ItemOriginMixin):
            items.extend([
                view.action("Resize", lambda: view.ui.editResize(self)),
            ])
        return items
