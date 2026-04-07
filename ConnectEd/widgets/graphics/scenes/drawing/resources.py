from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui  import QPen, QBrush, QPainterPath, QPolygonF, QPainterPathStroker

from .....app import settings

from .....core.defs  import WIDTH
from .....core.types import Direction

from ...items.base_pin import _PIN_SIZE, _PIN_DOT_SIZE, _PIN_CLK_SIZE, \
                              _EXT_ARROW_SIZE, _INT_ARROW_SIZE
from ...items.port import _PORT_SIZE

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingScene


class DrawingSceneResourcesMixin:
    """Shared resources."""

    resources = {}

    def initResources(self : "DrawingScene") -> None:
        self.resources |= \
            {
                "Grip" : {
                    "brush" : QBrush(),
                    "paths" : {
                        "UnfilledSquare"         : QPainterPath(),
                        "FilledSquare"           : QPainterPath(),
                        "UnfilledDiamond"        : QPainterPath(),
                        "UnfilledDiamondSquared" : QPainterPath(),
                        "FilledDiamond"          : QPainterPath(),
                        "FilledDiamondSquared"   : QPainterPath(),
                        "UnfilledCircle"         : QPainterPath(),
                        "UnfilledCircleSquared"  : QPainterPath(),
                        "FilledCircle"           : QPainterPath(),
                        "FilledCircleSquared"    : QPainterPath(),
                        "FilledArrow"            : QPainterPath()
                    }
                },
                "SymbolPin" : {
                    "dot"   : QPainterPath(),
                    "clock" : QPainterPath()
                },
                "SymbolPinArrow" : {
                    "in"  : QPainterPath(),
                    "out" : QPainterPath(),
                    "bi"  : QPainterPath()
                },
                "Entry" : {
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
        _symbolPinPaths(self.resources["SymbolPin"])
        self.updateResources()
        settings().changed.connect(self.updateResources)

    def updateResources(self : "DrawingScene") -> None:
        size = settings().get("theme/items/Entry/size")
        _pinExtArrowPaths(self.resources["SymbolPinArrow"], size)
        self.resources["Grip"]["brush"] = \
            QBrush(settings().get("theme/grip/color"))
        size = settings().get("theme/grip/size")
        _gripPaths(self.resources["Grip"]["paths"], size)
        for state in ["unconnected", "connected", "junction"]:
            self.resources["Entry"][state]["pen"] = \
                _getPen(f"Entry/{state}")
            self.resources["Entry"][state]["brush"] = \
                _getBrush(f"Entry/{state}")
            size = settings().get("theme/items/Entry/size")
            _nodePath(self.resources["Entry"], size)


def _gripPaths(d : dict, size : float) -> None:
    d.clear()
    # stroker for creating outlines
    stroker = QPainterPathStroker()
    stroker.setWidth(1.0)
    # square building blocks
    square_rect = QRectF(-size/2, -size/2, size, size)
    square_path = QPainterPath()
    square_path.addRect(square_rect)
    stroked_square = stroker.createStroke(square_path)
    # diamond building blocks
    diamond_poly = QPolygonF([
            QPointF(-size/2, 0),
            QPointF(0, -size/2),
            QPointF(size/2, 0),
            QPointF(0, size/2)
    ])
    diamond_path = QPainterPath()
    diamond_path.addPolygon(diamond_poly)
    diamond_path.closeSubpath()
    stroked_diamond = stroker.createStroke(diamond_path)
    # circle building blocks
    circle_path = QPainterPath()
    circle_path.addEllipse(square_rect)
    stroked_circle = stroker.createStroke(circle_path)
    # arrow building blocks
    arrow_path = QPainterPath()
    arrow_path.addPolygon(QPolygonF([
            QPointF(-size/2, -size/2),
            QPointF(size/2, 0),
            QPointF(-size/2, size/2)
    ]))
    # paths
    d["UnfilledSquare"] = stroked_square
    d["FilledSquare"] = square_path
    d["UnfilledDiamond"] = stroked_diamond
    d["UnfilledDiamondSquared"] = stroked_diamond.united(stroked_square)
    d["FilledDiamond"] = diamond_path
    d["FilledDiamondSquared"] = diamond_path.united(stroked_square)
    d["UnfilledCircle"] = stroked_circle
    d["UnfilledCircleSquared"] = stroked_circle.united(stroked_square)
    d["FilledCircle"] = circle_path
    d["FilledCircleSquared"] = circle_path.united(stroked_square)
    d["FilledArrow"] = arrow_path

def _symbolPinPath(d : dict, dot : bool, clock : bool) -> None:
    path = QPainterPath()
    path.moveTo(-_PIN_SIZE, 0)
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

def _symbolPinPaths(d : dict) -> None:
    d.clear()
    for dot in [False, True]:
        for clock in [False, True]:
            _symbolPinPath(d, dot, clock)

def _pinExtArrowPaths(d : dict, size : float) -> None:
    w = WIDTH
    wh = WIDTH / 2
    x1 = wh + w + _PIN_DOT_SIZE
    x2 = _PIN_SIZE - (size / 2)
    c = -((x1 + x2) / 2)  # center point
    sh = _EXT_ARROW_SIZE / 2
    sq = _EXT_ARROW_SIZE / 4
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

def _nodePath(d : dict, size : float) -> None:
    # unconnected = "X"
    path = QPainterPath()
    path.clear()
    path.moveTo(-size/2, -size/2)
    path.lineTo(size/2, size/2)
    path.moveTo(size/2, -size/2)
    path.lineTo(-size/2, size/2)
    path.closeSubpath()
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

def _getPen(path : str) -> QPen:
    return QPen(
        settings().get(f"theme/items/{path}/line/color"),
        settings().get(f"theme/items/{path}/line/width"),
        settings().get(f"theme/items/{path}/line/style")
    )

def _getBrush(path : str) -> QBrush:
    return QBrush(
        settings().get(f"theme/items/{path}/fill/color"),
        settings().get(f"theme/items/{path}/fill/style")
    )
