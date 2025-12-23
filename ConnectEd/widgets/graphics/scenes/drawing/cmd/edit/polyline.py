from typing import Self

from .. import CmdSceneItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .....scenes.drawing import DrawingScene
    from .....items.polyline import Polyline, PolySeg


class CmdEditPolylineClosed(CmdSceneItem):
    _item   : "Polyline"
    _before : bool
    _after  : bool
    _sweep  : float | None

    def __init__(
        self   : Self,
        scene  : "DrawingScene",
        item   : "Polyline",
        closed : bool,
        sweep  : float | None
    ):
        super().__init__(scene, item)
        self._item = item
        self._before = item.closed()
        self._after = closed
        self._sweep = sweep

    def redo(self : Self) -> None:
        if self._after:
            self._item.close(self._sweep)
        else:
            self._item.open()

    def undo(self : Self) -> None:
        if self._before:
            self._item.close(self._sweep)
        else:
            self._item.open()


class CmdEditPolySeg(CmdSceneItem):
    _item   : "PolySeg"
    _before : float | None
    _after  : float | None

    def __init__(
        self  : Self,
        scene : "DrawingScene",
        seg   : "PolySeg",
        sweep : float | None
    ):
        super().__init__(scene, seg)
        self._before = seg.sweep()
        self._after = sweep

    def redo(self : Self) -> None:
        self._item.setSweep(self._after)
        parent : "Polyline" = self._item.parentItem()
        parent.updatePath()

    def undo(self : Self) -> None:
        self._item.setSweep(self._before)
        parent : "Polyline" = self._item.parentItem()
        parent.updatePath()
