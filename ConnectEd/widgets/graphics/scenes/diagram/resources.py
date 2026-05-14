from typing import Self, Any

from PyQt6.QtCore import Qt, QLineF, QRectF
from PyQt6.QtGui  import QPen, QBrush, QPainterPath

from .....app import settings

from .....core.defs  import PITCH, WIDTH
from .....core.types import Direction

from ...items.node import NodeState, FreeNodeItem, FixedNodeItem
from ...items.port import PortItem, PortArrowItem

from ..drawing.resources import DrawingSceneResources, _getPen, _getBrush
from ..symbol.resources  import SymbolSceneResourcesMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DiagramScene


class DiagramSceneResources(DrawingSceneResources):
    _lines   : dict[type, QLineF] = {}
    _pens    : dict[type, dict[tuple[bool, ...], QPen]] = {}
    _brushes : dict[type, dict[bool, QBrush]] = {}
    _paths   : dict[type, dict[Direction, QPainterPath]] = {}

    def __init__(self : Self):
        self.update()
        settings().changed.connect(self.update)

    def update(self : Self):
        """Typically called after a settings change."""
        # free and fixed node
        for item_cls in [FreeNodeItem, FixedNodeItem]:
            item_name = item_cls.__name__.removesuffix("Item")
            self._pens[item_cls] = {}
            self._brushes[item_cls] = {}
            self._paths[item_cls] = {}
            size = settings().get(f"theme/items/{item_name}/size")
            for state in NodeState:
                state_str = state.value
                pen_normal = QPen(
                    settings().get(f"theme/items/{item_name}/{state_str}/pen/color"),
                    settings().get(f"theme/items/{item_name}/{state_str}/pen/width"),
                    settings().get(f"theme/items/{item_name}/{state_str}/pen/style")
                )
                pen_selected = QPen(pen_normal)
                pen_selected.setColor(settings().get("theme/selected/line"))  # TODO change to pen/color
                self._pens[item_cls][(state, False)] = pen_normal
                self._pens[item_cls][(state, True)] = pen_selected
                self._paths[item_cls][state] = self._nodePath(state, size)
                brush_normal = QBrush(
                    settings().get(f"theme/items/{item_name}/{state_str}/brush/color"),
                    settings().get(f"theme/items/{item_name}/{state_str}/brush/style")
                )
                brush_selected = QBrush(brush_normal)
                brush_selected.setColor(settings().get("theme/selected/fill"))  # TODO change to fill/color
                self._brushes[item_cls][(state, False)] = brush_normal
                self._brushes[item_cls][(state, True)] = brush_selected
        # port
        self._lines[PortItem] = QLineF(0, 0, PITCH, 0)
        self._pens[PortItem] = {}
        for bus in [False, True]:
            wire_bus = "bus" if bus else "wire"
            pen_normal = QPen(
                settings().get(f"theme/items/Port/pin/{wire_bus}/pen/color"),
                settings().get(f"theme/items/Port/pin/{wire_bus}/pen/width"),
                settings().get(f"theme/items/Port/pin/{wire_bus}/pen/style"),
                Qt.PenCapStyle.SquareCap
            )
            pen_selected = QPen(pen_normal)
            pen_selected.setColor(settings().get("theme/selected/line"))  # TODO change to pen/color
            self._pens[PortItem][(bus, False)] = pen_normal
            self._pens[PortItem][(bus, True)] = pen_selected
        # port arrow: path
        size = settings().get("theme/items/Port/arrow/size")
        self._paths[PortArrowItem] = {}
        for direction in Direction:
            port_arrow_dir = {
                Direction.NONE : "none",
                Direction.IN   : "left",
                Direction.OUT  : "right",
                Direction.BI   : "both"
            }
            self._paths[PortArrowItem][direction] = \
                self._arrowPath(size, port_arrow_dir[direction])
        # pens and brushes for items that are normal or selected
        for item_cls, settings_path in [
            ( PortArrowItem , "Port/arrow" )
        ]:
            pen_normal = QPen(
                settings().get(f"theme/items/{settings_path}/pen/color"),
                settings().get(f"theme/items/{settings_path}/pen/width"),
                settings().get(f"theme/items/{settings_path}/pen/style"),
                join=Qt.PenJoinStyle.MiterJoin
            )
            pen_selected = QPen(pen_normal)
            pen_selected.setColor(settings().get("theme/selected/line"))  # TODO change to pen/color
            self._pens[item_cls] = {}
            self._pens[item_cls][False] = pen_normal
            self._pens[item_cls][True] = pen_selected
            brush_normal = QBrush(
                settings().get(f"theme/items/{settings_path}/brush/color"),
                settings().get(f"theme/items/{settings_path}/brush/style")
            )
            brush_selected = QBrush(brush_normal)
            brush_selected.setColor(settings().get("theme/selected/fill"))  # TODO change to fill/color
            self._brushes[item_cls] = {}
            self._brushes[item_cls][False] = brush_normal
            self._brushes[item_cls][True] = brush_selected
        # DrawingSceneResources
        super().update()

    def line(self : Self, cls : type) -> QLineF:
        if cls not in self._lines: return super().line(cls)
        return self._lines[cls]

    def pen(self : Self, cls : type, key : bool | tuple) -> QPen:
        if cls not in self._pens: return super().pen(cls, key)
        return self._pens[cls][key]

    def brush(self : Self, cls : type, key : bool | tuple) -> QBrush:
        if cls not in self._brushes: return super().brush(cls, key)
        return self._brushes[cls][key]

    def path(self : Self, cls : type, key : Direction) -> QPainterPath:
        if cls not in self._paths: return super().path(cls, key)
        return self._paths[cls][key]

    def _arrowPath(self : Self, size: float, dir : str) -> QPainterPath:
        path = QPainterPath()
        if dir == "none":
            path.addRect(QRectF(-size/2, -size/2, size, size))
        elif dir == "left":
            path.lineTo(size, -size)
            path.lineTo(size * 2, -size)
            path.lineTo(size * 2, size)
            path.lineTo(size, size)
        elif dir == "right":
            path.moveTo(size * 2, 0)
            path.lineTo(size, -size)
            path.lineTo(0, -size)
            path.lineTo(0, size)
            path.lineTo(size, size)
        elif dir == "both":
            path.lineTo(size, -size)
            path.lineTo(size * 2, 0)
            path.lineTo(size, size)
        path.closeSubpath()
        return path

    def _nodePath(self : Self, state : NodeState, size : float) -> QPainterPath:
        path = QPainterPath()
        match state:
            case NodeState.UNCONNECTED:
                # square
                path.addRect(QRectF(-size/2, -size/2, size, size))
            case NodeState.CONNECTED:
                # diamond
                path.moveTo(-size/2, 0)
                path.lineTo(0, -size/2)
                path.lineTo(size/2, 0)
                path.lineTo(0, size/2)
                path.closeSubpath()
            case NodeState.JUNCTION:
                # circle
                path.addEllipse(QRectF(-size/2, -size/2, size, size))
            case _:
                raise ValueError(f"Invalid node state: {state}")
        return path


class DiagramSceneResourcesMixin(SymbolSceneResourcesMixin):
    """Shared resources."""

    def initResourcesDict(self : "Self | DiagramScene") -> None:
        super().initResourcesDict()
        self.resources |= \
            {
                "BlockPin" : QPainterPath(),
                "BlockPinArrow" : {
                    "in"  : QPainterPath(),
                    "out" : QPainterPath(),
                    "bi"  : QPainterPath()
                },
                "GatePin" : {
                    ( False , False ) : QPainterPath(),
                    ( False , True  ) : QPainterPath(),
                    ( True  , False ) : QPainterPath(),
                    ( True  , True  ) : QPainterPath()
                },
                "Tap" : {
                    "unresolved" : QPen(),
                    "scalar"     : QPen(),
                    "vector"     : QPen()
                },
                "FreeNode" : {
                    "unconnected" : {
                        "pen"   : QPen(),
                        "brush" : QBrush(),
                        "path"  : QPainterPath()
                    },
                    "connected" : {
                        "pen"   : QPen(),
                        "brush" : QBrush(),
                        "path"  : QPainterPath()
                    },
                    "junction" : {
                        "pen"   : QPen(),
                        "brush" : QBrush(),
                        "path"  : QPainterPath()
                    }
                },
                "FixedNode" : {
                    "unconnected" : {
                        "pen"   : QPen(),
                        "brush" : QBrush(),
                        "path"  : QPainterPath()
                    },
                    "connected" : {
                        "pen"   : QPen(),
                        "brush" : QBrush(),
                        "path"  : QPainterPath()
                    },
                    "junction" : {
                        "pen"   : QPen(),
                        "brush" : QBrush(),
                        "path"  : QPainterPath()
                    }
                }
            }

    def updateResources(self : "Self | DiagramScene") -> None:
        # drawing and symbol resources
        super().updateResources()
        # block pin
        _blockPinPath(self.resources["BlockPin"])
        _blockPinArrowPaths(self.resources["BlockPinArrow"])
        # gate pin
        _gatePinPaths(self.resources["GatePin"])
        # tap
        for state in ["unresolved", "scalar", "vector"]:
            pen = _getPen(f"Tap/{state}")
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            self.resources["Tap"][state] = pen


def _blockPinPath(path : QPainterPath) -> None:
    pin_size = PITCH
    path.clear()
    path.moveTo(-pin_size, 0)
    path.lineTo(0, 0)

def _blockPinArrowPaths(d : dict) -> None:
    s = settings().get("theme/items/BlockPinArrow/size")
    h = s / 2
    # in
    path = QPainterPath()
    path.moveTo(0, -h)
    path.lineTo(h, -h)
    path.lineTo(s,  0)
    path.lineTo(h, +h)
    path.lineTo(0, +h)
    path.closeSubpath()
    d[Direction.IN.value] = path
    # out
    path = QPainterPath()
    path.moveTo(s, -h)
    path.lineTo(h, -h)
    path.lineTo(0,  0)
    path.lineTo(h, +h)
    path.lineTo(s, +h)
    path.closeSubpath()
    d[Direction.OUT.value] = path
    # bi
    path = QPainterPath()
    path.moveTo(0,  0)
    path.lineTo(h, -h)
    path.lineTo(s,  0)
    path.lineTo(h, +h)
    path.closeSubpath()
    d[Direction.BI.value] = path

def _gatePinPath(d : dict, dot : bool, clock : bool) -> None:
    pin_size = PITCH
    dot_size = settings().get("theme/items/SymbolPinDot/size")
    clk_size = settings().get("theme/items/SymbolPinClk/size")
    path = QPainterPath()
    path.moveTo(-pin_size, 0)
    if dot:
        path.lineTo(-(WIDTH + dot_size), 0)
        path.arcTo(
            -(WIDTH + dot_size),
            -dot_size / 2,
            dot_size,
            dot_size,
            180,
            360
        )
        path.moveTo(-WIDTH, 0)
        path.lineTo(0, 0)
    else:
        path.lineTo(0, 0)
    if clock:
        path.moveTo(0, -clk_size / 2)
        path.lineTo(clk_size, 0)
        path.lineTo(0, clk_size / 2)
        path.closeSubpath()
    d[(dot, clock)] = path

def _gatePinPaths(d : dict) -> None:
    d.clear()
    for dot in [False, True]:
        for clock in [False, True]:
            _gatePinPath(d, dot, clock)

def _tapPath(d : dict) -> None:
    path = QPainterPath()
    path.moveTo(0, 0)
    path.lineTo(PITCH, PITCH)
    path.lineTo(2*PITCH, PITCH)
    d["path"] = path
