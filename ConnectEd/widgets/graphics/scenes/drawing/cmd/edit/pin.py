from typing      import Self
from dataclasses import dataclass

from .......core.check import checked

from .. import CmdSceneItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .......core.types     import Direction
    from .....scenes.drawing   import DrawingScene
    from .....items.port_pin   import PortPinMixin
    from .....items.symbol_pin import SymbolPinItem


class CmdEditPortPin(CmdSceneItem):
    @dataclass
    class PortPinState:
        name      : str
        direction : Direction

    _item   : "PortPinMixin"
    _before : PortPinState
    _after  : PortPinState

    @checked
    def __init__(
        self      : Self,
        scene     : "DrawingScene",
        item      : "PortPinMixin",
        name      : str,
        direction : "Direction"
    ) -> None:
        super().__init__(scene, item)
        self._before = self.PortPinState(item.name(), item.direction())
        self._after  = self.PortPinState(name, direction)

    @checked
    def redo(self : Self) -> None:
        self._item.setName(self._after.name)
        self._item.setDirection(self._after.direction)
        self._item.update()

    @checked
    def undo(self : Self) -> None:
        self._item.setName(self._before.name)
        self._item.setDirection(self._before.direction)
        self._item.update()


class CmdEditSymbolPinDot(CmdSceneItem):
    _item   : "SymbolPinItem"
    _before : bool
    _after  : bool

    @checked
    def __init__(
        self   : Self,
        scene  : "DrawingScene",
        item   : "SymbolPinItem",
        enable : bool
    ) -> None:
        super().__init__(scene, item)
        self._before = item.dot()
        self._after = enable

    @checked
    def redo(self : Self) -> None:
        self._item.setDot(self._after)
        self._item.update()

    @checked
    def undo(self : Self) -> None:
        self._item.setDot(self._before)
        self._item.update()


class CmdEditSymbolPinClock(CmdSceneItem):
    _item   : "SymbolPinItem"
    _before : bool
    _after  : bool

    @checked
    def __init__(
        self   : Self,
        scene  : "DrawingScene",
        item   : "SymbolPinItem",
        enable : bool
    ) -> None:
        super().__init__(scene, item)
        self._before = item.clock()
        self._after = enable

    @checked
    def redo(self : Self) -> None:
        self._item.setClock(self._after)
        self._item.update()

    @checked
    def undo(self : Self) -> None:
        self._item.setClock(self._before)
        self._item.update()
