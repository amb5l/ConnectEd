from PyQt6.QtCore import QRectF
from PyQt6.QtGui  import QPainterPath

from .....app import settings

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingScene


_PIN_LEN = 10 # documentation - DO NOT CHANGE


class DrawingScenePathsMixin:
    """Container for shared paths."""

    paths : dict[str, dict[str, QPainterPath]]

    def initPaths(self : "DrawingScene") -> None:
        self.paths = {
            "Grip"   : QPainterPath(),
            "Origin" : QPainterPath(),
            "Port" : {
                "in"  : QPainterPath(),
                "out" : QPainterPath(),
                "bi"  : QPainterPath()
            },
            "BlockPinArrow" : {
                "in"  : QPainterPath(),
                "out" : QPainterPath(),
                "bi"  : QPainterPath()
            },
            "SymbolPinArrow" : {
                "in"  : QPainterPath(),
                "out" : QPainterPath(),
                "bi"  : QPainterPath()
            },
            "WireVertex" : QPainterPath()
        }
        self.updatePaths()
        settings().changed.connect(self.updatePaths)

    def updatePaths(self : "DrawingScene") -> None:
        self._gripPath ( self.paths["Grip"] )
        self._originPath ( self.paths["Origin"] )
        size = settings().get("theme/elements/Port/size")
        self._portInPath  ( self.paths["Port"][ "in"  ] , size )
        self._portOutPath ( self.paths["Port"][ "out" ] , size )
        self._portBiPath  ( self.paths["Port"][ "bi"  ] , size )
        size = settings().get("theme/elements/BlockPinArrow/size")
        self._pinArrowInPath  ( self.paths["BlockPinArrow"][ "in"  ] , size )
        self._pinArrowOutPath ( self.paths["BlockPinArrow"][ "out" ] , size )
        self._pinArrowBiPath  ( self.paths["BlockPinArrow"][ "bi"  ] , size )
        size = settings().get("theme/elements/SymbolPinArrow/size")
        self._pinArrowInPath  ( self.paths["SymbolPinArrow"][ "in"  ] , size )
        self._pinArrowOutPath ( self.paths["SymbolPinArrow"][ "out" ] , size )
        self._pinArrowBiPath  ( self.paths["SymbolPinArrow"][ "bi"  ] , size )
        size = settings().get("theme/elements/WireVertex/size")
        self._wireVertexPath( self.paths["WireVertex"] , size )

    def _gripPath(self : "DrawingScene", path : QPainterPath) -> None:
        size = settings().get("theme/grip/size")
        path.clear()
        path.addEllipse(QRectF(-size/2, -size/2, size, size))

    def _originPath(self : "DrawingScene", path : QPainterPath) -> None:
        size = settings().get("theme/origin/size")
        path.clear()
        path.addRect(QRectF(-size/2, -size/2, size, size))

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

    def _pinArrowInPath(
        self : "DrawingScene",
        path : QPainterPath,
        size : float
    ) -> None:
        h = size / 2 ; q = h / 2 ; c = -_PIN_LEN / 2
        path.clear()
        path.moveTo(c-q, -h)
        path.lineTo(c+q,  0)
        path.lineTo(c-q, +h)
        path.closeSubpath()

    def _pinArrowOutPath(
        self : "DrawingScene",
        path : QPainterPath,
        size : float
    ) -> None:
        h = size / 2 ; q = h / 2 ; c = -_PIN_LEN / 2
        path.clear()
        path.moveTo(c+q, -h)
        path.lineTo(c-q,  0)
        path.lineTo(c+q, +h)

    def _pinArrowBiPath(
        self : "DrawingScene",
        path : QPainterPath,
        size : float
    ) -> None:
        h = size / 2 ; q = h / 2 ; c = -_PIN_LEN / 2
        path.clear()
        path.moveTo(c,   -h)
        path.lineTo(c+h,  0)
        path.lineTo(c,   +h)
        path.closeSubpath()

    def _wireVertexPath(
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