from typing import Self

from PyQt6.QtCore import Qt, QPointF, QLineF, QRectF
from PyQt6.QtGui  import QPen, QBrush, \
                         QPolygonF, QPainterPath, QPainterPathStroker

from .....app import settings

from .....core.defs  import PITCH, WIDTH
from .....core.types import Direction

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingScene


class DrawingSceneResources:
    # class attributes
    _PIN_PATH_ITEMS = ["SymbolPin"]
    _PIN_LINE_ITEMS = {}
    _PIN_ARROW_ITEMS = {"SymbolPinArrow" : (False, False)} # : int, in_left

    # instance attributes
    _pens    : dict[str, dict[tuple[bool, ...], QPen]] = {}
    _brushes : dict[str, dict[bool, QBrush]] = {}
    _lines   : dict[str, QLineF] = {}
    _paths   : dict[str, dict[Direction, QPainterPath]] = {}

    def update(self : Self) -> None:
        # pin pens
        pin_items = self._PIN_PATH_ITEMS + list(self._PIN_LINE_ITEMS.keys())
        for item_name in pin_items:
            self._pens[item_name] = {}
            for bus in [False, True]:
                wire_bus = "bus" if bus else "wire"
                pen_normal, pen_selected = self._getPens(
                    f"theme/items/{item_name}/pin/{wire_bus}/pen"
                )
                self._pens[item_name][(bus, False)] = pen_normal
                self._pens[item_name][(bus, True)] = pen_selected
        # pin lines
        for item_name, line_x in self._PIN_LINE_ITEMS.items():
            self._lines[item_name] = QLineF(0, 0, line_x, 0)
        # pin paths
        for item_name in self._PIN_PATH_ITEMS:
            self._paths[item_name] = {}
            for clock in [False, True]:
                for dot in [False, True]:
                    self._paths[item_name][(clock, dot)] = \
                        self._extPinPath(item_name, dot, clock)
        # pin arrow paths, pens and brushes
        for item_name, (int_ext, in_left) in self._PIN_ARROW_ITEMS.items():
            pin_item_name = item_name.removesuffix("Arrow")
            settings_path = f"theme/items/{pin_item_name}"
            self._paths[item_name] = {}
            for direction in Direction:
                arrow_dir = {
                    Direction.NONE : "none",
                    Direction.IN   : "left"  if in_left else "right",
                    Direction.OUT  : "right" if in_left else "left",
                    Direction.BI   : "both"
                }
                size = settings().get(f"{settings_path}/arrow/size")
                if int_ext:
                    path = self._intArrowPath(size, arrow_dir[direction])
                else:
                    path = self._extArrowPath(
                        size,
                        settings().get(f"{settings_path}/pin/dot/size"),
                        arrow_dir[direction]
                    )
                self._paths[item_name][direction] = path
            pen_normal, pen_selected = \
                self._getPens(
                    f"{settings_path}/arrow/pen",
                    cap_style=Qt.PenCapStyle.FlatCap
                )
            pen_selected = QPen(pen_normal)
            pen_selected.setColor(settings().get("theme/selected/line"))
            self._pens[item_name] = {}
            self._pens[item_name][False] = pen_normal
            self._pens[item_name][True] = pen_selected
            brush_normal, brush_selected = \
                self._getBrushes(f"{settings_path}/arrow/brush")
            self._brushes[item_name] = {}
            self._brushes[item_name][False] = brush_normal
            self._brushes[item_name][True] = brush_selected

    def pen(self : Self, item_name : str, key : bool | tuple) -> QPen:
        if item_name not in self._pens:
            raise ValueError(f"No pen defined for item {item_name}")
        return self._pens[item_name][key]

    def brush(self : Self, item_name : str, key : bool | tuple) -> QBrush:
        if item_name not in self._brushes:
            raise ValueError(f"No brush defined for item {item_name}")
        return self._brushes[item_name][key]

    def line(self : Self, item_name : str) -> QLineF:
        if item_name not in self._lines:
            raise ValueError(f"No line defined for item {item_name}")
        return self._lines[item_name]

    def path(self : Self, item_name : str, key : Direction) -> QPainterPath:
        if item_name not in self._paths:
            raise ValueError(f"No path defined for item {item_name}")
        return self._paths[item_name][key]

    def _getPens(
        self          : Self,
        settings_path : str,
        join_style    : Qt.PenJoinStyle = Qt.PenJoinStyle.MiterJoin,
        cap_style     : Qt.PenCapStyle = Qt.PenCapStyle.FlatCap
    ) -> tuple[QPen, QPen]:
        pen_normal = QPen(
            settings().get(f"{settings_path}/color"),
            settings().get(f"{settings_path}/width"),
            settings().get(f"{settings_path}/style")
        )
        pen_normal.setJoinStyle(join_style)
        pen_normal.setCapStyle(cap_style)
        pen_selected = QPen(pen_normal)
        pen_selected.setColor(settings().get("theme/selected/line"))
        return pen_normal, pen_selected

    def _getBrushes(self : Self, settings_path : str) -> tuple[QBrush, QBrush]:
        brush_normal = QBrush(
            settings().get(f"{settings_path}/color"),
            settings().get(f"{settings_path}/style")
        )
        brush_selected = QBrush(brush_normal)
        brush_selected.setColor(settings().get("theme/selected/fill"))
        return brush_normal, brush_selected

    def _extPinPath(
        self      : Self,
        item_name : str,
        dot       : bool,
        clock     : bool
    ) -> QPainterPath:
        dot_size = settings().get(f"theme/items/{item_name}/pin/dot/size")
        clk_size = settings().get(f"theme/items/{item_name}/pin/clock/size")
        path = QPainterPath()
        path.moveTo(-PITCH, 0)
        if dot:
            path.lineTo(-(WIDTH + dot_size), 0)
            path.arcTo(
                -(WIDTH + dot_size), -dot_size / 2,
                dot_size, dot_size,
                180, 360
            )
            path.moveTo(-WIDTH, 0)
        path.lineTo(WIDTH / 2, 0)
        if clock:
            path.moveTo(0, -clk_size / 2)
            path.lineTo(clk_size, 0)
            path.lineTo(0, clk_size / 2)
            path.closeSubpath()
        return path

    def _extArrowPath(
        self       : Self,
        arrow_size : float,
        dot_size   : float,
        dir        : str
    ) -> QPainterPath:
        """
        External style arrow e.g. for gate and symbol pins.
        """
        path = QPainterPath()
        wh = WIDTH / 2
        c = -6.25
        sh = arrow_size / 2
        sq = arrow_size / 4
        if dir == "left":
            path.moveTo( c + sq      , -sh )
            path.lineTo( c - sq      ,   0 )
            path.lineTo( c + sq      , +sh )
        elif dir == "right":
            path.moveTo( c - sq      , -sh )
            path.lineTo( c + sq      ,   0 )
            path.lineTo( c - sq      , +sh )
        elif dir == "both":
            path.moveTo( c - wh      , -sh )
            path.lineTo( c - wh - sh ,   0 )
            path.lineTo( c - wh      , +sh )
            path.closeSubpath()
            path.moveTo( c + wh      , -sh )
            path.lineTo( c + wh + sh ,   0 )
            path.lineTo( c + wh      , +sh )
        path.closeSubpath()
        return path

    def _intArrowPath(self : Self, size: float, dir : str) -> QPainterPath:
        """
        Internal style arrow e.g. for ports and block pins.
        """
        h = size / 2
        path = QPainterPath()
        if dir == "none":
            path.addRect(QRectF(-h, -h, h * 2, h * 2))
        elif dir == "left":
            path.lineTo(h, -h)
            path.lineTo(h * 2, -h)
            path.lineTo(h * 2, h)
            path.lineTo(h, h)
        elif dir == "right":
            path.moveTo(h * 2, 0)
            path.lineTo(h, -h)
            path.lineTo(0, -h)
            path.lineTo(0, h)
            path.lineTo(h, h)
        elif dir == "both":
            path.lineTo(h, -h)
            path.lineTo(h * 2, 0)
            path.lineTo(h, h)
        path.closeSubpath()
        return path

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
