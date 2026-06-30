from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui     import QAction

from ....core.check import checked
from ....core.types import RectHandleId, DataKind

from ..properties import InherentProperty

from .role import FunctionalItem

from .base_rect import BaseRectangleItem

from .part import PartItemMixin

from .mixin.edge_loc import ItemLocParentMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.diagram import DiagramView


class BlockItem(
    FunctionalItem,
    ItemLocParentMixin,
    PartItemMixin,
    BaseRectangleItem
):
    # class attributes
    _ORIGIN = RectHandleId.TOP_LEFT
    _PROPERTIES = \
        PartItemMixin._PROPERTIES_PART | \
        {
            "Path" : InherentProperty["BlockItem"](
                kind   = DataKind.STR,
                getter = lambda self: self.path(),
                setter = lambda self, value: self.setPath(value)
            )
        } | \
        BaseRectangleItem._PROPERTIES
    _XML_CHILDREN = frozenset({"BlockPin", "PropertyText"})

    # instance attributes
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
        super().__init__(p1, p2, fresh)

    def path(self : Self) -> str:
        return self._path

    @checked
    def setPath(self : Self, path : str) -> None:
        self._path = path
        self.properties.signalChanges("Path")

    def onGeometryChanged(self : Self) -> None:
        super().onGeometryChanged()
        # TODO: reposition pins
        #for item in self.childItems():
        #    if isinstance(item, Pin):
        #        item.onPositionChanged()

    @checked
    def ctxMenuItems(
        self : Self,
        view : DiagramView,
        spos : QPointF
    ) -> list[QAction | QMenu]:
        return [
            view.action("Add Pin...", view.placeBlockPin),
            view.separator(),
            view.action("Appearance...", lambda: view.editAppearance(self)),
            view.action("Properties...", lambda: view.editItemProperties(self))
        ]

    def ctxMenuAddPin(
        self    : Self,
        checked : bool,
        view    : DiagramView
    ) -> None:
        pass
