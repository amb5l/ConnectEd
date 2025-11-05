from typing import Self

from ....core.defs import PITCH

from .symbol_pin import SymbolPin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.drawing import DrawingScene
    from .gate import Gate


class GatePin(SymbolPin):
    # instance attributes
    _length : float

    def __init__(self : Self, parent : "Gate | None" = None) -> None:
        self._length = PITCH
        super().__init__(parent)

    @property
    def inverted(self : Self) -> bool:
        return self._dot

    @inverted.setter
    def inverted(self : Self, value : bool) -> None:
        self._dot = value
        self._setPath()

    def length(self : Self) -> float:
        return self._length

    def setLength(self : Self, length : float) -> None:
        self._length = length

    def _setPath(self : Self, scene : "DrawingScene | None" = None) -> None:
        super()._setPath(scene)
        if self._length != PITCH:
            path = self.path()
            path.setElementPositionAt(0, -self._length, 0)
            self.setPath(path)
