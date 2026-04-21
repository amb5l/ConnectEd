from typing import Self

from PyQt6.QtGui  import QPainterPath

from .....app import settings

from .....core.defs  import PITCH, WIDTH
from .....core.types import Direction

from ..drawing.resources import DrawingSceneResourcesMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import SymbolScene


class SymbolSceneResourcesMixin(DrawingSceneResourcesMixin):
    """Shared resources."""

    def initResourcesDict(self : "Self | SymbolScene") -> None:
        super().initResourcesDict()
        self.resources |= \
            {
                "SymbolPin" : {
                    ( False , False ) : QPainterPath(),
                    ( False , True  ) : QPainterPath(),
                    ( True  , False ) : QPainterPath(),
                    ( True  , True  ) : QPainterPath()
                },
                "SymbolPinArrow" : {
                    "in"  : QPainterPath(),
                    "out" : QPainterPath(),
                    "bi"  : QPainterPath()
                }
            }

    def updateResources(self : "Self | SymbolScene") -> None:
        super().updateResources()
        _symbolPinPaths(self.resources["SymbolPin"])
        _symbolPinArrowPaths(self.resources["SymbolPinArrow"])

def _symbolPinPath(d : dict, dot : bool, clock : bool) -> None:
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

def _symbolPinPaths(d : dict) -> None:
    d.clear()
    for dot in [False, True]:
        for clock in [False, True]:
            _symbolPinPath(d, dot, clock)

def _symbolPinArrowPaths(d : dict) -> None:
    pin_size = PITCH
    arrow_size = settings().get("theme/items/SymbolPinArrow/size")
    dot_size = settings().get("theme/items/SymbolPinDot/size")
    w = WIDTH
    wh = WIDTH / 2
    x1 = wh + w + dot_size
    x2 = pin_size - (arrow_size / 2)
    c = -((x1 + x2) / 2)  # center point
    sh = arrow_size / 2
    sq = arrow_size / 4
    # in
    path = QPainterPath()
    path.moveTo(c - sq , -sh)
    path.lineTo(c + sq ,   0)
    path.lineTo(c - sq , +sh)
    path.closeSubpath()
    d[Direction.IN.value] = path
    # out
    path = QPainterPath()
    path.moveTo(c + sq , -sh)
    path.lineTo(c - sq ,   0)
    path.lineTo(c + sq , +sh)
    path.closeSubpath()
    d[Direction.OUT.value] = path
    # bi
    path = QPainterPath()
    path.moveTo(c - wh      , -sh)
    path.lineTo(c - wh - sh ,  0)
    path.lineTo(c - wh      , +sh)
    path.closeSubpath()
    path.moveTo(c + wh      , -sh)
    path.lineTo(c + wh + sh ,   0)
    path.lineTo(c + wh      , +sh)
    path.closeSubpath()
    d[Direction.BI.value] = path
