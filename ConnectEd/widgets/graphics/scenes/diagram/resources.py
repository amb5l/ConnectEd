from typing import Self

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui  import QPen, QBrush, QPainterPath

from .....app import settings

from .....core.defs  import PITCH, WIDTH
from .....core.types import Direction

from ..drawing.resources import _getPen, _getBrush
from ..symbol.resources  import SymbolSceneResourcesMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DiagramScene


class DiagramSceneResourcesMixin(SymbolSceneResourcesMixin):
    """Shared resources."""

    def initResourcesDict(self : "Self | DiagramScene") -> None:
        super().initResourcesDict()
        self.resources |= \
            {
                "Port" : {
                    "in"  : QPainterPath(),
                    "out" : QPainterPath(),
                    "bi"  : QPainterPath()
                },
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
                "PinNode" : {
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
                "TapNode" : {
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
        # port
        _portPaths(self.resources["Port"])
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
        # nodes
        for node_type in ["FreeNode", "PinNode", "TapNode"]:
            for state in ["unconnected", "connected", "junction"]:
                self.resources[node_type][state]["pen"] = \
                    _getPen(f"{node_type}/{state}")
                self.resources[node_type][state]["brush"] = \
                    _getBrush(f"{node_type}/{state}")
                size = settings().get(f"theme/items/{node_type}/size")
                _nodePath(self.resources[node_type], size)


def _portInPath(path : QPainterPath, size : float) -> None:
    p = PITCH
    s = size / 2
    path.clear()
    path.moveTo(0, 0)
    path.lineTo(p, 0)
    path.lineTo(s+p, -s)
    path.lineTo(s*2+p, -s)
    path.lineTo(s*2+p, s)
    path.lineTo(s+p, s)
    path.lineTo(p, 0)

def _portOutPath(path : QPainterPath, size : float) -> None:
    p = PITCH
    s = size / 2
    path.clear()
    path.lineTo(p, 0)
    path.moveTo(s*2+p, 0)
    path.lineTo(s+p, -s)
    path.lineTo(p, -s)
    path.lineTo(p, s)
    path.lineTo(s+p, s)
    path.lineTo(p, 0)

def _portBiPath(path : QPainterPath, size : float) -> None:
    p = PITCH
    s = size / 2
    path.clear()
    path.moveTo(0, 0)
    path.lineTo(p, 0)
    path.lineTo(s+p, -s)
    path.lineTo(2*s+p, 0)
    path.lineTo(s+p, s)
    path.lineTo(p, 0)
    path.closeSubpath()

def _portPaths(d : dict) -> None:
    size = settings().get("theme/items/Port/size")
    _portInPath(d["in"], size)
    _portOutPath(d["out"], size)
    _portBiPath(d["bi"], size)

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

def _nodePath(d : dict, size : float) -> None:
    # unconnected = square
    path = QPainterPath()
    path.addRect(QRectF(-size/2, -size/2, size, size))
    d["unconnected"]["path"] = path
    # connected = diamond
    path = QPainterPath()
    path.moveTo(-size/2, 0)
    path.lineTo(0, -size/2)
    path.lineTo(size/2, 0)
    path.lineTo(0, size/2)
    path.closeSubpath()
    d["connected"]["path"] = path
    # junction = circle
    path = QPainterPath()
    path.addEllipse(QRectF(-size/2, -size/2, size, size))
    d["junction"]["path"] = path
