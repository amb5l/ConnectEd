from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui  import QPainterPath, QPolygonF

from .....app import settings

from .....core.defs import WIDTH, PITCH

from ...items import SignalDirection

from ...items.base_pin import _PIN_DOT_SIZE, _PIN_CLK_SIZE, \
                              _EXT_ARROW_SIZE, _INT_ARROW_SIZE
from ...items.entry    import _ENTRY_SIZE

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingScene


class DrawingScenePathsMixin:
    """Shared paths."""

    paths : dict[str, dict[str, QPainterPath]]

    def initPaths(self : "DrawingScene") -> None:
        self.paths = {
            "Grip" : {},
            "Port" : {
                "in"  : QPainterPath(),
                "out" : QPainterPath(),
                "bi"  : QPainterPath()
            },
            "BlockPin" : QPainterPath(),
            "BlockPinArrow" : {},
            "SymbolPin" : {},
            "SymbolPinArrow" : {},
            "ConnVtx" : QPainterPath()
        }
        self._blockPinPath(self.paths["BlockPin"])
        self._symbolPinPaths(self.paths["SymbolPin"])
        self._pinIntArrowPaths(self.paths["BlockPinArrow"])
        self._pinExtArrowPaths(self.paths["SymbolPinArrow"])
        self.updatePaths()
        settings().changed.connect(self.updatePaths)

    def updatePaths(self : "DrawingScene") -> None:
        size = settings().get("theme/grip/size")
        self._gripPaths(self.paths["Grip"], size)
        size = settings().get("theme/items/Port/size")
        self._portInPath(self.paths["Port"]["in"], size)
        self._portOutPath(self.paths["Port"]["out"], size)
        self._portBiPath(self.paths["Port"]["bi"], size)
        size = settings().get("theme/items/ConnVtx/size")
        self._connVtxPath(self.paths["ConnVtx"], size)

    def _gripPaths(self : "DrawingScene", d : dict, size : float) -> None:
        d.clear()
        # square
        path = QPainterPath()
        path.addRect(QRectF(-size/2, -size/2, size, size))
        d["Square"] = path
        # circle
        path = QPainterPath()
        path.addEllipse(QRectF(-size/2, -size/2, size, size))
        d["Circle"] = path
        # diamond
        path = QPainterPath()
        path.addPolygon(QPolygonF([
                QPointF(-size/2, 0),
                QPointF(0, -size/2),
                QPointF(size/2, 0),
                QPointF(0, size/2)
        ]))
        d["Diamond"] = path
        # arrow
        path = QPainterPath()
        path.addPolygon(QPolygonF([
                QPointF(-size/2, -size/2),
                QPointF(size/2, 0),
                QPointF(-size/2, size/2)
        ]))
        d["Arrow"] = path

    def _portInPath(
        self : "DrawingScene",
        path : QPainterPath,
        size : float
    ) -> None:
        s = size / 2
        path.clear()
        path.moveTo(0, 0)
        path.lineTo(s, -s)
        path.lineTo(s*2, -s)
        path.lineTo(s*2, s)
        path.lineTo(s, s)
        path.closeSubpath()

    def _portOutPath(
        self : "DrawingScene",
        path : QPainterPath,
        size : float
    ) -> None:
        s = size / 2
        path.clear()
        path.moveTo(s*2, 0)
        path.lineTo(s, -s)
        path.lineTo(0, -s)
        path.lineTo(0, s)
        path.lineTo(s, s)
        path.closeSubpath()

    def _portBiPath(
        self : "DrawingScene",
        path : QPainterPath,
        size : float
    ) -> None:
        s = size / 2
        path.clear()
        path.moveTo(0, 0)
        path.lineTo(s, -s)
        path.lineTo(2*s, 0)
        path.lineTo(s, s)
        path.closeSubpath()

    def _blockPinPath(self : "DrawingScene", path : QPainterPath) -> None:
        path.clear()
        path.moveTo(-PITCH, 0)
        path.lineTo(0, 0)

    def _symbolPinPath(
        self      : "DrawingScene",
        d         : dict,
        dot       : bool,
        clock     : bool
    ) -> None:
        path = QPainterPath()
        path.moveTo(-PITCH, 0)
        if dot:
            path.lineTo(-(WIDTH + _PIN_DOT_SIZE), 0)
            path.arcTo(
                -(WIDTH + _PIN_DOT_SIZE),
                -_PIN_DOT_SIZE / 2,
                _PIN_DOT_SIZE,
                _PIN_DOT_SIZE,
                180,
                360
            )
            path.moveTo(-WIDTH, 0)
            path.lineTo(0, 0)
        else:
            path.lineTo(0, 0)
        if clock:
            path.moveTo(0, -_PIN_CLK_SIZE / 2)
            path.lineTo(_PIN_CLK_SIZE, 0)
            path.lineTo(0, _PIN_CLK_SIZE / 2)
            path.closeSubpath()
        d[(dot, clock)] = path

    def _symbolPinPaths(self : "DrawingScene", d : dict) -> None:
        d.clear()
        for dot in [False, True]:
            for clock in [False, True]:
                self._symbolPinPath(d, dot, clock)

    def _pinIntArrowPaths(self : "DrawingScene", d : dict) -> None:
        s = _INT_ARROW_SIZE
        h = s / 2
        # in
        path = QPainterPath()
        path.moveTo(0 , -h)
        path.lineTo(h , -h)
        path.lineTo(s ,  0)
        path.lineTo(h , +h)
        path.lineTo(0 , +h)
        path.closeSubpath()
        d[SignalDirection.IN.value] = path
        # out
        path = QPainterPath()
        path.moveTo(s , -h)
        path.lineTo(h , -h)
        path.lineTo(0 ,  0)
        path.lineTo(h , +h)
        path.lineTo(s , +h)
        path.closeSubpath()
        d[SignalDirection.OUT.value] = path
        # bi
        path = QPainterPath()
        path.moveTo(0 ,  0)
        path.lineTo(h , -h)
        path.lineTo(s ,  0)
        path.lineTo(h , +h)
        path.closeSubpath()
        d[SignalDirection.BI.value] = path

    def _pinExtArrowPaths(self : "DrawingScene", d : dict) -> None:
        w = WIDTH
        wh = WIDTH / 2
        x1 = wh + w + _PIN_DOT_SIZE
        x2 = PITCH - (_ENTRY_SIZE / 2)
        c = -((x1 + x2) / 2)  # center point
        sh = _EXT_ARROW_SIZE / 2
        sq = _EXT_ARROW_SIZE / 4
        # in
        path = QPainterPath()
        path.moveTo(c - sq , -sh)
        path.lineTo(c + sq ,   0)
        path.lineTo(c - sq , +sh)
        path.closeSubpath()
        d[SignalDirection.IN.value] = path
        # out
        path = QPainterPath()
        path.moveTo(c + sq , -sh)
        path.lineTo(c - sq ,   0)
        path.lineTo(c + sq , +sh)
        path.closeSubpath()
        d[SignalDirection.OUT.value] = path
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
        d[SignalDirection.BI.value] = path

    def _connVtxPath(
        self : "DrawingScene",
        path : QPainterPath,
        size : float
    ) -> None:
        s = size / 2
        path.clear()
        path.moveTo(-s, 0)
        path.lineTo(0, -s)
        path.lineTo(s, 0)
        path.lineTo(0, s)
        path.closeSubpath()

    def _polyVtxPath(
        self : "DrawingScene",
        path : QPainterPath,
        size : float
    ) -> None:
        s = size / 2
        path.clear()
        path.moveTo(-s, 0)
        path.lineTo(0, -s)
        path.lineTo(s, 0)
        path.lineTo(0, s)
        path.closeSubpath()
