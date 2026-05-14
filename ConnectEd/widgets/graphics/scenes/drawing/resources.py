from typing import Self, Any

from PyQt6.QtCore import Qt, QPointF, QLineF, QRectF
from PyQt6.QtGui  import QColor, QPen, QBrush, \
                         QPolygonF, QPainterPath, QPainterPathStroker

from .....app import settings

from .....core.types import Direction

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingScene


class DrawingSceneResources:
    def update(self : Self) -> None:
        pass

    def line(self : Self, cls : type) -> QLineF:
        match cls:
            case _:
                raise ValueError(f"No line defined for class {cls}")

    def pen(self : Self, cls : type, key : bool | tuple) -> QPen:
        match cls:
            case _:
                raise ValueError(f"No pen defined for class {cls}")

    def brush(self : Self, cls : type, key : bool | tuple) -> QBrush:
        match cls:
            case _:
                raise ValueError(f"No pen defined for class {cls}")

    def path(self : Self, cls : type, key : Direction) -> QPainterPath:
        match cls:
            case _:
                raise ValueError(f"No path defined for class {cls}")


class DrawingSceneResourcesMixin:
    """Shared resources."""

    resources : dict

    def initResources(self : "Self | DrawingScene") -> None:
        self.initResourcesDict()
        self.updateResources()
        settings().changed.connect(self.updateResources)

    def initResourcesDict(self : "Self | DrawingScene") -> None:
        self.resources = \
            {
                "Outline" : {
                    "pen" : QPen()
                },
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
                }
            }

    def updateResources(self : "Self | DrawingScene") -> None:
        self.resources["Outline"]["pen"] = QPen(
            settings().get("theme/selected/line"),
            settings().get("display/select/outline/width"),
            settings().get("display/select/outline/style")
        )
        self.resources["Grip"]["brush"] = \
            QBrush(settings().get("theme/grip/color"))
        _gripPaths(self.resources["Grip"]["paths"])


def _gripPaths(d : dict) -> None:
    size = settings().get("theme/grip/size")
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

__all__ = ["_getPen", "_getBrush"]
