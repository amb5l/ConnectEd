from typing import Self, Protocol, TypeVar

from typing_extensions import runtime_checkable

from PyQt6.QtCore    import QPointF, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QPen, QBrush

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....core.types   import HandleId
    from ..scenes.diagram import DiagramScene
    from ..quill          import Quill
    from .handle          import HandleItem


T = TypeVar("T", covariant=True)


class FreshItemConstructor(Protocol[T]):
    def __call__(self, *, fresh: bool = ...) -> T: ...


@runtime_checkable
class SetPenProtocol(Protocol):

    def setPen(self : Self, pen : QPen) -> None: ...


@runtime_checkable
class SetBrushProtocol(Protocol):

    def setBrush(self : Self, brush : QBrush) -> None: ...


@runtime_checkable
class SetQuillProtocol(Protocol):

    def setQuill(self : Self, quill : Quill) -> None: ...


@runtime_checkable
class ItemHandlesProtocol(Protocol):

    @classmethod
    def handleIdType(cls) -> type[HandleId]: ...

    def handles(self : Self) -> dict[HandleId, HandleItem]: ...

    def getHandle(self : Self, id : HandleId | str) -> HandleItem: ...


@runtime_checkable
class FromXmlProtocol(Protocol):

    @classmethod
    def fromXml(cls, xr : QXmlStreamReader) -> QGraphicsItem: ...


@runtime_checkable
class OnSceneChangedProtocol(Protocol):

    def onSceneChanged(self : Self, scene : DiagramScene | None) -> None: ...


@runtime_checkable
class OnParentChangedProtocol(Protocol):

    def onParentChanged(self : Self, parent : QGraphicsItem | None) -> None: ...


@runtime_checkable
class OnScenePositionChangedProtocol(Protocol):

    def onScenePositionChanged(self : Self, pos : QPointF) -> None: ...


@runtime_checkable
class OnPositionChangedProtocol(Protocol):

    def onPositionChanged(self : Self, pos : QPointF) -> None: ...


@runtime_checkable
class OnRotationChangedProtocol(Protocol):

    def onRotationChanged(self : Self, angle : float) -> None: ...


@runtime_checkable
class OnSelectionChangedProtocol(Protocol):

    def onSelectionChanged(self : Self, selected : bool) -> None: ...


@runtime_checkable
class OnGeometryChangedProtocol(Protocol):

    def onGeometryChanged(self : Self) -> None: ...


@runtime_checkable
class OnTextChangedProtocol(Protocol):

    def onTextChanged(self : Self) -> None: ...


@runtime_checkable
class OnSceneOrientationChangedProtocol(Protocol):

    def onSceneOrientationChanged(self : Self) -> None: ...


@runtime_checkable
class MoveHandleByProtocol(Protocol):

    def moveHandleBy(
        self : Self,
        id   : HandleId,
        d    : QPointF
    ) -> None: ...


@runtime_checkable
class ResizeHandleByProtocol(Protocol):

    def resizeHandleBy(
        self : Self,
        id   : HandleId,
        d    : QPointF
    ) -> None: ...


@runtime_checkable
class SetPointsProtocol(Protocol):

    def setPoints(self : Self, p1 : QPointF, p2 : QPointF) -> None: ...
