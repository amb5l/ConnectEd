from __future__ import annotations

from typing import Self

from .......core.check import checked

from .....items.polyline import PolylineItem, PolySegItem

from .. import CmdSceneItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .....scenes.diagram import DiagramScene


class CmdEditPolylineClosed(CmdSceneItem[PolylineItem]):
    _before : bool
    _after  : bool
    _sweep  : float | None

    @checked
    def __init__(
        self   : Self,
        scene  : DiagramScene,
        item   : PolylineItem,
        closed : bool,
        sweep  : float | None
    ) -> None:
        super().__init__(scene, item)
        self._item   = item
        self._before = item.closed()
        self._after  = closed
        self._sweep  = sweep

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


class CmdEditPolySeg(CmdSceneItem[PolySegItem]):
    _before : float | None
    _after  : float | None

    @checked
    def __init__(
        self  : Self,
        scene : DiagramScene,
        seg   : PolySegItem,
        sweep : float | None
    ) -> None:
        super().__init__(scene, seg)
        self._before = seg.sweep()
        self._after  = sweep

    @checked
    def redo(self : Self) -> None:
        self._item.setSweep(self._after)
        if not isinstance(parent := self._item.parentItem(), PolylineItem):
            raise TypeError("Bad parent")
        parent.updatePath()

    @checked
    def undo(self : Self) -> None:
        self._item.setSweep(self._before)
        if not isinstance(parent := self._item.parentItem(), PolylineItem):
            raise TypeError("Bad parent")
        parent.updatePath()
