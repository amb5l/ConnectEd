from typing      import Self
from dataclasses import dataclass

from .. import CmdSceneItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .....scenes.drawing   import DrawingScene
    from .....items            import SignalDirection
    from .....items.port_pin   import PortPinMixin
    from .....items.symbol_pin import SymbolPinItem


class CmdEditPortPin(CmdSceneItem):
    @dataclass
    class PortPinState:
        name      : str
        direction : "SignalDirection"

    _item   : "PortPinMixin"
    _before : PortPinState
    _after  : PortPinState

    def __init__(
        self      : Self,
        scene     : "DrawingScene",
        item      : "PortPinMixin",
        name      : str,
        direction : "SignalDirection"
    ):
        super().__init__(scene, item)
        self._before = self.PortPinState(item.name(), item.direction())
        self._after  = self.PortPinState(name, direction)

    def redo(self : Self) -> None:
        self._item.setName(self._after.name)
        self._item.setDirection(self._after.direction)
        self._item.update()

    def undo(self : Self) -> None:
        self._item.setName(self._before.name)
        self._item.setDirection(self._before.direction)
        self._item.update()


class CmdEditSymbolPinDot(CmdSceneItem):
    _item   : "SymbolPinItem"
    _before : bool
    _after  : bool

    def __init__(
        self   : Self,
        scene  : "DrawingScene",
        item   : "SymbolPinItem",
        enable : bool
    ):
        super().__init__(scene, item)
        self._before = item.dot()
        self._after = enable

    def redo(self : Self) -> None:
        self._item.setDot(self._after)
        self._item.update()

    def undo(self : Self) -> None:
        self._item.setDot(self._before)
        self._item.update()


class CmdEditSymbolPinClock(CmdSceneItem):
    _item   : "SymbolPinItem"
    _before : bool
    _after  : bool

    def __init__(
        self : Self,
        scene : "DrawingScene",
        item : "SymbolPinItem",
        enable : bool
    ):
        super().__init__(scene, item)
        self._before = item.clock()
        self._after = enable

    def redo(self : Self) -> None:
        self._item.setClock(self._after)
        self._item.update()

    def undo(self : Self) -> None:
        self._item.setClock(self._before)
        self._item.update()
