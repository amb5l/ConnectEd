from __future__ import annotations

from typing import Self

from .......core.check import checked

from .. import CmdSceneItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .....scenes.drawing import DrawingScene
    from .....items.polyline import PolylineItem, PolySegItem


class CmdEditPolylineClosed(CmdSceneItem):
    _item   : PolylineItem
    _before : bool
    _after  : bool
    _sweep  : float | None

    @checked
    def __init__(
        self   : Self,
        scene  : DrawingScene,
        item   : PolylineItem,
        closed : bool,
        sweep  : float | None
    ) -> None:
        super().__init__(scene, item)
        self._item = item
        self._before = item.closed()
        self._after = closed
        self._sweep = sweep

    @checked
    def redo(self : Self) -> None:
        if self._after:
            self._item.close(self._sweep)
        else:
            self._item.open()

    @checked
    def undo(self : Self) -> None:
        if self._before:
            self._item.close(self._sweep)
        else:
            self._item.open()


class CmdEditPolySeg(CmdSceneItem):
    _item   : PolySegItem
    _before : float | None
    _after  : float | None

    @checked
    def __init__(
        self  : Self,
        scene : DrawingScene,
        seg   : PolySegItem,
        sweep : float | None
    ) -> None:
        super().__init__(scene, seg)
        self._before = seg.sweep()
        self._after = sweep

    @checked
    def redo(self : Self) -> None:
        self._item.setSweep(self._after)
        parent : PolylineItem = self._item.parentItem()
        parent.updatePath()

    @checked
    def undo(self : Self) -> None:
        self._item.setSweep(self._before)
        parent : PolylineItem = self._item.parentItem()
        parent.updatePath()
