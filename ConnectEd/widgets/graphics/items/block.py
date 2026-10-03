from __future__ import annotations

from typing            import Self
from typing_extensions import override

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui     import QAction

from ....core.check import checked
from ....core.types import RectHandleId, DataKind

from ..properties import PropertySpec

from .role      import FunctionalItem
from .base_rect import BaseRectangleItem
from .part      import PartItemMixin

from .mixin.edge_loc import ItemEdgeLocParentMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.diagram import DiagramView


class BlockItem(
    FunctionalItem,
    ItemEdgeLocParentMixin,
    PartItemMixin,
    BaseRectangleItem
):
    # class attributes
    _ORIGIN = RectHandleId.TOP_LEFT
    _PROPERTIES_PATH = {
        "Path" : PropertySpec["BlockItem"](
            kind   = DataKind.STR,
            getter = lambda self: self.path(),
            setter = lambda self, value: self.setPath(value)
        )
    }
    _PROPERTIES = \
        PartItemMixin._PROPERTIES_PART | \
        _PROPERTIES_PATH | \
        BaseRectangleItem._PROPERTIES
    _XML_CHILDREN = frozenset({"BlockPin", "Label"})

    # instance attributes
    _path : str
    _line_color = None  # enable per-item appearance control
    _fill_color = None  # enable per-item appearance control
    _fill_style = None  # enable per-item appearance control

    @checked
    def __init__(
        self  : Self,
        p1    : QPointF | None = None,
        p2    : QPointF | None = None,
        fresh : bool = True
    ) -> None:
        self.initPart()
        self._path = ""
        super().__init__(p1, p2, fresh)

    def path(self : Self) -> str:
        return self._path

    @checked
    def setPath(self : Self, path : str) -> None:
        self._path = path
        self.properties["Path"].notify()

    @override
    @checked
    def setWidth(self : Self, width : float | int) -> None:
        width, _height = self.clipEdgeSize(float(width), self.height())
        super().setWidth(width)

    @override
    @checked
    def setHeight(self : Self, height : float | int) -> None:
        _width, height = self.clipEdgeSize(self.width(), float(height))
        super().setHeight(height)

    @override
    @checked
    def moveHandleBy(self : Self, id : RectHandleId, d : QPointF) -> None:
        d = self.clipHandleDelta(id, d)
        self.rewriteEdgeOffsets(id, d)
        super().moveHandleBy(id, d)

    @override
    def onGeometryChanged(self : Self) -> None:
        super().onGeometryChanged()
        self.refreshEdgeLocs()

    @override
    @checked
    def ctxMenuItems(
        self : Self,
        view : DiagramView,
        spos : QPointF
    ) -> list[QAction | QMenu]:
        return [
            view.action("Add Pin...", lambda: view.placeBlockPin(self)),
            view.separator(),
            view.action("Appearance...", lambda: view.editAppearance(self)),
            view.action("Properties...", lambda: view.editItemProperties(self))
        ]

