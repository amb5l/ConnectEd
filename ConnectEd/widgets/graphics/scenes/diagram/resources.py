from PyQt6.QtGui  import QPen, QBrush, QPainterPath

from .....app import settings

from .....core.types import Direction

from ...items.base_pin import _PIN_SIZE, _INT_ARROW_SIZE
from ...items.port     import _PORT_SIZE

from ..drawing.resources import DrawingSceneResourcesMixin, \
                                _nodePath, _getPen, _getBrush

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DiagramScene


class DiagramSceneResourcesMixin(DrawingSceneResourcesMixin):
    """Shared resources."""

    def initResources(self : "DiagramScene") -> None:
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
                "Vertex" : {
                    "unconnected" : {
                        "pen"   : QPen(),
                        "brush" : QBrush(),
                        "path"  : QPainterPath()
                    },
                    "connected" :  {
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
        _blockPinPath(self.resources["BlockPin"])
        super().initResources()

    def updateResources(self : "DiagramScene") -> None:
        _portInPath(self.resources["Port"]["in"])
        _portOutPath(self.resources["Port"]["out"])
        _portBiPath(self.resources["Port"]["bi"])
        _blockPinArrowPaths(self.resources["BlockPinArrow"])
        for state in ["unconnected", "connected", "junction"]:
            self.resources["Vertex"][state]["pen"] = \
                _getPen(f"Vertex/{state}")
            self.resources["Vertex"][state]["brush"] = \
                _getBrush(f"Vertex/{state}")
            size = settings().get("theme/items/Vertex/size")
            _nodePath(self.resources["Vertex"], size)
        super().updateResources()

def _portInPath(path : QPainterPath) -> None:
    p = _PIN_SIZE
    s = _PORT_SIZE / 2
    path.clear()
    path.moveTo(0, 0)
    path.lineTo(p, 0)
    path.lineTo(s+p, -s)
    path.lineTo(s*2+p, -s)
    path.lineTo(s*2+p, s)
    path.lineTo(s+p, s)
    path.lineTo(p, 0)

def _portOutPath(path : QPainterPath) -> None:
    p = _PIN_SIZE
    s = _PORT_SIZE / 2
    path.clear()
    path.lineTo(p, 0)
    path.moveTo(s*2+p, 0)
    path.lineTo(s+p, -s)
    path.lineTo(p, -s)
    path.lineTo(p, s)
    path.lineTo(s+p, s)
    path.lineTo(p, 0)

def _portBiPath(path : QPainterPath) -> None:
    p = _PIN_SIZE
    s = _PORT_SIZE / 2
    path.clear()
    path.moveTo(0, 0)
    path.lineTo(p, 0)
    path.lineTo(s+p, -s)
    path.lineTo(2*s+p, 0)
    path.lineTo(s+p, s)
    path.lineTo(p, 0)
    path.closeSubpath()

def _blockPinPath(path : QPainterPath) -> None:
    path.clear()
    path.moveTo(-_PIN_SIZE, 0)
    path.lineTo(0, 0)

def _blockPinArrowPaths(d : dict) -> None:
    s = _INT_ARROW_SIZE
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
