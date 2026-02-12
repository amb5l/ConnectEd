from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui     import QAction

from ....core.types import EdgeLoc, Edge, RectHandleId

from ..properties import PropertyTextSpec, InherentProperty

from .base_rect import BaseRectangleItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing import DrawingView


class BlockItem(BaseRectangleItem):
    # class attributes
    _PROPERTIES = {
        "Label" : InherentProperty(
            kind   = "str",
            valid  = lambda self: self._label != "",
            getter = lambda self: self._label,
            setter = lambda self, value: setattr(self, "_label", value)
        ),
        "Name" : InherentProperty(
            kind   = "str",
            valid  = lambda self: self._name != "",
            getter = lambda self: self._name,
            setter = lambda self, value: setattr(self, "_name", value)
        ),
        "Path" : InherentProperty(
            kind   = "str",
            valid  = lambda self: self._path != "",
            getter = lambda self: self._path,
            setter = lambda self, value: setattr(self, "_path", value)
        )
    } | BaseRectangleItem._PROPERTIES
    _PROPERTY_TEXTS = {
        "Label" : PropertyTextSpec(
            cleat=RectHandleId.TOP_LEFT, origin=RectHandleId.BOTTOM_LEFT
        ),
        "Name"  : PropertyTextSpec(
            cleat=RectHandleId.BOTTOM_LEFT, origin=RectHandleId.TOP_LEFT
        )
    }

    # instance attributes
    _label : str
    _name  : str
    _path  : str

    def __init__(
        self  : Self,
        p1    : QPointF | None = None,
        p2    : QPointF | None = None,
        fresh : bool = True
    ) -> None:
        self._label = ""
        self._name = ""
        self._path = ""
        super().__init__(p1, p2, fresh)

    def onGeometryChange(self : Self) -> None:
        super().onGeometryChange()
        # TODO: reposition pins
        #for item in self.childItems():
        #    if isinstance(item, Pin):
        #        item.onPositionChange()

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        return [
            view.action("Add Pin...", view.ui.placeBlockPin),
            view.separator(),
            view.action("Appearance...", lambda: view.ui.editAppearance(self)),
            view.action("Properties...", lambda: view.ui.editItemProperties(self))
        ]

    def pos2loc(self : Self, pos : QPointF) -> EdgeLoc:
        rect = self.rect()
        w = rect.width()
        h = rect.height()
        c = c = self.mapToParent(rect.center())  # scene pos of rectangle center
        r = pos - c  # pos relative to rectangle center
        hq = False if r.x() == 0 or abs(r.y()/r.x()) > abs(h/w) else True
        if hq:
            offset = min(max(r.y(), -h/2), h/2) + h/2
            edge = Edge.LEFT if r.x() <= 0 else Edge.RIGHT
        else:
            offset = min(max(r.x(), -w/2), w/2) + w/2
            edge = Edge.TOP if r.y() <= 0 else Edge.BOTTOM
        return EdgeLoc(edge, offset)

    def loc2pos(self : Self, loc : EdgeLoc) -> QPointF:
        match loc.edge:
            case Edge.LEFT:
                return QPointF(0, loc.offset)
            case Edge.RIGHT:
                return QPointF(self.rect().width(), loc.offset)
            case Edge.TOP:
                return QPointF(loc.offset, 0)
            case Edge.BOTTOM:
                return QPointF(loc.offset, self.rect().height())
            case _:
                raise ValueError(f"Invalid edge: {loc.edge}")

    def loc2peri(self : Self, loc : EdgeLoc) -> float:
        rect = self.rect()
        w = rect.width()
        h = rect.height()
        d = loc.offset
        if loc.edge == Edge.LEFT:
            return d
        elif loc.edge == Edge.BOTTOM:
            return h + d
        elif loc.edge == Edge.RIGHT:
            return h + w + (h - d)
        elif loc.edge == Edge.TOP:
            return h + w + h + (w - d)
        else:
            raise ValueError(f"Invalid edge: {loc.edge}")

    def peri2loc(self : Self, peri : float) -> EdgeLoc:
        rect = self.rect()
        w = rect.width()
        h = rect.height()
        p = 2 * (w + h)
        peri = peri % p if p > 0 else 0
        if peri < h:
            return EdgeLoc(Edge.LEFT, peri)
        elif peri < h + w:
            return EdgeLoc(Edge.BOTTOM, peri - h)
        elif peri < h + w + h:
            return EdgeLoc(Edge.RIGHT, h - (peri - h - w))
        else:
            return EdgeLoc(Edge.TOP, w - (peri - h - w - h))

    def locDelta(self : Self, loc1 : EdgeLoc, loc2 : EdgeLoc) -> float:
        rect = self.rect()
        w = rect.width()
        h = rect.height()
        p = 2 * (w + h)
        d = self.loc2peri(loc2) - self.loc2peri(loc1)
        if d >= 0: # CCW
            ccw_d = d % p
            cw_d = p - ccw_d
        else: # CW
            cw_d = -d % p
            ccw_d = p - cw_d
        return -cw_d if cw_d < ccw_d else ccw_d

    def locOffset(
        self   : Self,
        loc    : EdgeLoc,
        offset : float,
        corner : int
    ) -> EdgeLoc:
        rect = self.rect()
        w = rect.width()
        h = rect.height()
        def edgeLen(edge : Edge) -> float:
            return h if edge in [Edge.LEFT, Edge.RIGHT] else w
        def edgeNextCCW(edge : Edge) -> Edge:
            return \
                Edge.BOTTOM if edge == Edge.LEFT   else \
                Edge.RIGHT  if edge == Edge.BOTTOM else \
                Edge.TOP    if edge == Edge.RIGHT  else \
                Edge.LEFT   if edge == Edge.TOP    else \
                Edge.UNDEFINED
        def edgeNextCW(edge : Edge) -> Edge:
            return \
                Edge.TOP    if edge == Edge.LEFT   else \
                Edge.RIGHT  if edge == Edge.TOP    else \
                Edge.BOTTOM if edge == Edge.RIGHT  else \
                Edge.LEFT   if edge == Edge.BOTTOM else \
                Edge.UNDEFINED
        loc = self.peri2loc(self.loc2peri(loc) + offset)
        if offset >= 0 and corner == +1: # CCW
            if (loc.edge in [Edge.LEFT, Edge.BOTTOM] and loc.offset == edgeLen(loc.edge)) \
            or (loc.edge in [Edge.RIGHT, Edge.TOP] and loc.offset == 0):
                loc.edge = edgeNextCCW(loc.edge)
                loc.offset = edgeLen(loc.edge) \
                    if loc.edge in [Edge.RIGHT, Edge.TOP] else 0
        elif offset < 0 and corner == -1: # CW
            if (loc.edge in [Edge.TOP, Edge.RIGHT] and loc.offset == edgeLen(loc.edge)) \
            or (loc.edge in [Edge.BOTTOM, Edge.LEFT] and loc.offset == 0):
                loc.edge = edgeNextCW(loc.edge)
                loc.offset = edgeLen(loc.edge) \
                    if loc.edge in [Edge.BOTTOM, Edge.LEFT] else 0
        return loc

    def ctxMenuAddPin(
        self    : Self,
        checked : bool,
        view    : "DrawingView"
    ) -> None:
        pass
