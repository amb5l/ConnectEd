from typing import Self

from PyQt6.QtCore    import QPointF, QXmlStreamWriter
from PyQt6.QtWidgets import QGraphicsItem, QMenu
from PyQt6.QtGui     import QAction, QPainterPath

from ....core.defs  import PITCH
from ....core.types import BlockPinHandleId, DataKind

from ..properties import InherentProperty

from .mixin.pos    import ItemPosMixin
from .mixin.rotate import ItemRotateMixin
from .mixin.line   import ItemLineMixin

from .port_pin import PortPinMixin
from .base_pin import BasePinItem, BasePinDotMixin, BasePinClockMixin, _PIN_CLK_SIZE

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing import DrawingView
    from ..scenes.drawing import DrawingScene


class GatePinItem(
    ItemPosMixin,
    ItemRotateMixin,
    BasePinDotMixin,
    BasePinClockMixin,
    BasePinItem
):
    # class attributes
    _PROPERTIES = \
        {
            "Name" : InherentProperty(
                kind   = DataKind.STR,
                getter = lambda self: self._name,
                setter = lambda self, value: setattr(self, "_name", value)
            )
        } | \
        PortPinMixin._PROPERTIES_DIR | \
        BasePinDotMixin._PROPERTIES_DOT | \
        BasePinClockMixin._PROPERTIES_CLOCK | \
        ItemPosMixin._PROPERTIES_POS | \
        ItemRotateMixin._PROPERTIES_ROTATE | \
        ItemLineMixin._PROPERTIES_LINE

    # instance attributes
    _length : float

    def __init__(
        self   : Self,
        parent : QGraphicsItem | None = None,
        fresh  : bool = True  # unused
    ) -> None:
        self._length = PITCH
        super().__init__(parent)

    def inverted(self : Self) -> bool:
        return self._dot

    def setInverted(self : Self, value : bool) -> None:
        self._dot = value
        self._setPath()

    def length(self : Self) -> float:
        return self._length

    def setLength(self : Self, length : float) -> None:
        self._length = length
        self._entry.setPos(-self._length, 0)  # move entry
        self._setPath()  # adjust pin path

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        return [
            view.action(
                "Active Low",
                lambda: view.ui.editSymbolPinDot(self, not self._dot),
                checked=self._dot
            )
        ]

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        pass  # exclude from XML

    def _setPath(self : Self, scene : "DrawingScene | None" = None) -> None:
        if scene is None:
            if (scene := self.scene()) is None:
                return
        key = (self._dot, self._clock)
        path = scene.paths["SymbolPin"][key]
        self._handles[BlockPinHandleId.NAME].setPos(QPointF(
            self._PIN_NAME_OFFSET + (_PIN_CLK_SIZE if self._clock else 0), 0
        ))
        if self._length != PITCH:
            path = QPainterPath(path)  # copy shared path
            path.setElementPositionAt(0, -self._length, 0)
        self.setPath(path)
