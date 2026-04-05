from typing import Self, TypeVar, Generic, Protocol, overload

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsItem

from .....core.defs import PITCH

from .....core.types import HandleId, RectHandleId, LineHandleId, \
                            BlockPinHandleId, SymbolPinHandleId, DataKind

from ..handle import HandleItem

from .origin import ItemOriginMixin
from .grip   import ItemGripMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..port_pin import PortPinMixin


class RectItemProtocol(Protocol):
    @overload
    def setPoints(self : Self, p1 : QPointF, p2 : QPointF) -> None: ...

    @overload
    def setPoints(
        self : Self,
        x1 : float | int,
        y1 : float | int,
        x2 : float | int,
        y2 : float | int
    ) -> None: ...


class LineItemProtocol(Protocol):
    def setP1(self : Self, pos : QPointF) -> None: ...
    def setP2(self : Self, pos : QPointF) -> None: ...


T = TypeVar("T", bound="HandleId")

class ItemHandlesMixin(ItemGripMixin, Generic[T]):

    @classmethod
    def handleIdType(cls) -> type[T]:
        raise NotImplementedError

    @classmethod
    def handleIdKind(cls) -> DataKind:
        raise NotImplementedError

    def handles(self : Self) -> dict[T, "HandleItem"]:
        return self._handles

    def getHandle(self : Self, id : T) -> "HandleItem":
        return self._handles[id]

    def moveHandleBy(self : Self, id : T, d : QPointF) -> None:
        raise NotImplementedError("Subclass must implement this method")


class ItemRectHandlesMixin(ItemHandlesMixin[RectHandleId]):
    @classmethod
    def handleIdType(cls) -> type[RectHandleId]:
        return RectHandleId

    @classmethod
    def handleIdKind(cls) -> DataKind:
        return DataKind.RECT_HANDLE

    # instance attributes
    _handles : dict[RectHandleId, "HandleItem"]

    def initHandles(self : Self) -> None:
        self._handles = {}
        resize_kind = getattr(self, "_RESIZE_KIND", "resize")
        for id in RectHandleId:
            kind = "move" if id == RectHandleId.MIDDLE_CENTER else resize_kind
            handle = HandleItem(id=id, kind=kind, parent=self)
            self._handles[id] = handle

    def handleRect(self : Self) -> QRectF:
        raise NotImplementedError("Subclass must implement this method")

    def updateHandlePositions(self : Self | ItemOriginMixin) -> None:
        if not hasattr(self, "_handles"):
            return
        rect = self.handleRect()
        x0 = rect.topLeft().x()
        y0 = rect.topLeft().y()
        w = rect.width()
        h = rect.height()
        for id in RectHandleId:
            name = id.value
            x = 1.0 if "Right" in name else 0.5 if "Center" in name else 0.0
            y = 1.0 if "Bottom" in name else 0.5 if "Middle" in name else 0.0
            self._handles[id].setPos(QPointF(x0 + (x * w), y0 + (y * h)))
        if hasattr(self, "origin"):
            self.updateOrigin()

    def moveHandleBy(
        self : Self | QGraphicsItem | RectItemProtocol,
        id   : RectHandleId,
        d    : QPointF
    ) -> None:
        p1 = self.pos() - self.transformOriginPoint()
        p2 = p1 + self.rect().bottomRight()
        match id:
            case RectHandleId.TOP_LEFT:
                self.setPoints(p1 + d, p2)
            case RectHandleId.TOP_CENTER:
                self.setPoints(p1.x(), p1.y() + d.y(), p2.x(), p2.y())
            case RectHandleId.TOP_RIGHT:
                self.setPoints(p1.x(), p1.y() + d.y(), p2.x() + d.x(), p2.y())
            case RectHandleId.MIDDLE_LEFT:
                self.setPoints(p1.x() + d.x(), p1.y(), p2.x(), p2.y())
            case RectHandleId.MIDDLE_CENTER:
                self.moveBy(d)
            case RectHandleId.MIDDLE_RIGHT:
                self.setPoints(p1.x(), p1.y(), p2.x() + d.x(), p2.y())
            case RectHandleId.BOTTOM_LEFT:
                self.setPoints(p1.x() + d.x(), p1.y(), p2.x(), p2.y() + d.y())
            case RectHandleId.BOTTOM_CENTER:
                self.setPoints(p1.x(), p1.y(), p2.x(), p2.y() + d.y())
            case RectHandleId.BOTTOM_RIGHT:
                self.setPoints(p1, p2 + d)
            case _:
                raise ValueError(f"Invalid handle: {id}")


class ItemLineHandlesMixin(ItemHandlesMixin[LineHandleId]):
    @classmethod
    def handleIdType(cls) -> type[LineHandleId]:
        return LineHandleId

    @classmethod
    def handleIdKind(cls) -> DataKind:
        return DataKind.LINE_HANDLE

    # instance attributes
    _handles : dict[LineHandleId, "HandleItem"]

    def initHandles(self : Self) -> None:
        self._handles = {
            LineHandleId.P1 : HandleItem(
                id     = LineHandleId.P1,
                pos    = QPointF(0, 0),
                kind   = "resize",
                parent = self
            ),
            LineHandleId.P2 : HandleItem(
                id     = LineHandleId.P2,
                pos    = QPointF(0, 0),
                kind   = "resize",
                parent = self
            )
        }

    def moveHandleBy(
        self : Self | LineItemProtocol,
        id   : LineHandleId,
        d    : QPointF
    ) -> None:
        match id:
            case LineHandleId.P1:
                self.setP1(self.p1() + d)
            case LineHandleId.P2:
                self.setP2(self.p2() + d)
            case _:
                raise ValueError(f"Invalid handle: {id}")


class ItemBasePinHandlesMixin:
    # instance attributes
    _handles : dict[SymbolPinHandleId, "HandleItem"]

    def initHandles(self : "Self | PortPinMixin") -> None:
        self._handles = {
            SymbolPinHandleId.ORIGIN : HandleItem(
                id     = SymbolPinHandleId.ORIGIN,
                pos    = QPointF(0, 0),
                kind   = "move",
                parent = self
            ),
            SymbolPinHandleId.ENTRY : HandleItem(
                id     = SymbolPinHandleId.ENTRY,
                pos    = QPointF(-PITCH, 0),
                kind   = "move",
                parent = self
            ),
            SymbolPinHandleId.NAME : HandleItem(
                id     = SymbolPinHandleId.NAME,
                pos    = QPointF(self._PIN_NAME_OFFSET, 0),
                kind   = "move",
                parent = self
            )
        }

class ItemBlockPinHandlesMixin(
    ItemBasePinHandlesMixin,
    ItemHandlesMixin[BlockPinHandleId]
):
    @classmethod
    def handleIdType(cls) -> type[BlockPinHandleId]:
        return BlockPinHandleId

    @classmethod
    def handleIdKind(cls) -> DataKind:
        return DataKind.BLOCK_PIN_HANDLE


class ItemSymbolPinHandlesMixin(
    ItemBasePinHandlesMixin,
    ItemHandlesMixin[SymbolPinHandleId]
):
    @classmethod
    def handleIdType(cls) -> type[SymbolPinHandleId]:
        return SymbolPinHandleId

    @classmethod
    def handleIdKind(cls) -> DataKind:
        return DataKind.SYMBOL_PIN_HANDLE

    def moveHandleBy(self : Self | QGraphicsItem, _, d : QPointF) -> None:
        """Move the entire pin when any grip is dragged."""
        self.setPos(self.pos() + d)
