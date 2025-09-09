from typing import Self

from PyQt6.QtGui     import QPainterPath

from ..... import hub


_PIN_LEN = 10 # documentation - DO NOT CHANGE


class DrawingScenePathsMixin:
    """Container for shared paths."""

    paths : dict[str, dict[str, QPainterPath]]


    def initPaths(self : Self) -> None:
        self.paths = {
            "Port": {
                "in"  : QPainterPath(),
                "out" : QPainterPath(),
                "bi"  : QPainterPath()
            },
            "BlockPinArrow": {
                "in"  : QPainterPath(),
                "out" : QPainterPath(),
                "bi"  : QPainterPath()
            },
            "SymbolPinArrow": {
                "in"  : QPainterPath(),
                "out" : QPainterPath(),
                "bi"  : QPainterPath()
            }
        }
        self.updatePaths()

    def updatePaths(self : Self) -> None:
        (
            self.paths["Port"]["in"],
            self.paths["Port"]["out"],
            self.paths["Port"]["bi"]
        ) = self._buildPortPaths(
            hub.settings.getTheme("elements/Port/size")
        )
        (
            self.paths["BlockPinArrow"]["in"],
            self.paths["BlockPinArrow"]["out"],
            self.paths["BlockPinArrow"]["bi"]
        ) = self._buildPinArrowPaths(
            hub.settings.getTheme("elements/BlockPinArrow/size")
        )
        (
            self.paths["SymbolPinArrow"]["in"],
            self.paths["SymbolPinArrow"]["out"],
            self.paths["SymbolPinArrow"]["bi"]
        ) = self._buildPinArrowPaths(
            hub.settings.getTheme("elements/SymbolPinArrow/size")
        )

    def _buildPortPaths(
        self : Self,
        size : float
    ) -> tuple[QPainterPath, QPainterPath, QPainterPath]:
        s = size / 2
        _in = QPainterPath()
        _in.moveTo(0, 0)
        _in.lineTo(s, -s)
        _in.lineTo(s*2, -s)
        _in.lineTo(s*2, s)
        _in.lineTo(s, s)
        _in.closeSubpath()
        _out = QPainterPath()
        _out.moveTo(s*2, 0)
        _out.lineTo(s, -s)
        _out.lineTo(0, -s)
        _out.lineTo(0, s)
        _out.lineTo(s, s)
        _out.closeSubpath()
        _bi = QPainterPath()
        _bi.moveTo(0, 0)
        _bi.lineTo(s, -s)
        _bi.lineTo(2*s, 0)
        _bi.lineTo(s, s)
        _bi.closeSubpath()
        return _in, _out, _bi

    def _buildPinArrowPaths(
        self : Self,
        size : float
    ) -> tuple[QPainterPath, QPainterPath, QPainterPath]:
        h = size / 2
        q = h / 2
        c = -_PIN_LEN / 2
        _in = QPainterPath()
        _in.moveTo(c-q, -h)
        _in.lineTo(c+q,  0)
        _in.lineTo(c-q, +h)
        _out = QPainterPath()
        _out.moveTo(c+q, -h)
        _out.lineTo(c-q,  0)
        _out.lineTo(c+q, +h)
        _bi = QPainterPath()
        c = c + 1
        _bi.moveTo(c,   -h)
        _bi.lineTo(c+h,  0)
        _bi.lineTo(c,   +h)
        c = c - 2
        _bi.moveTo(c,   -h)
        _bi.lineTo(c-h,  0)
        _bi.lineTo(c,   +h)
        return _in, _out, _bi
