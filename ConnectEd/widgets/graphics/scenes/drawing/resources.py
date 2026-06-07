from typing import Self

from PyQt6.QtCore import Qt, QPointF, QLineF, QRectF
from PyQt6.QtGui  import QPen, QBrush, QTransform, \
                         QPolygonF, QPainterPath

from .....app import settings

from .....core.defs  import PITCH, WIDTH
from .....core.types import Direction

from ...quill import Quill

from ...items.grip import GripShape


class DrawingSceneResources:
    # class attributes
    _PEN_ITEMS = ["Rectangle", "Ellipse", "Block", "Line", "Polyline"]
    _BRUSH_ITEMS = ["Rectangle", "Ellipse", "Block", "Polyline"]
    _QUILL_ITEMS = ["Text", "PropertyText"]
    _PIN_PATH_ITEMS = ["SymbolPin"]
    _PIN_LINE_ITEMS = {}
    _PIN_ARROW_ITEMS = {"SymbolPinArrow" : (False, False)} # : int, in_left

    # instance attributes
    _pens    : dict[str, QPen | dict[tuple[bool, ...], QPen]] = {}
    _brushes : dict[str, QBrush | dict[bool, QBrush]] = {}
    _quills  : dict[str, Quill | dict[bool, Quill]] = {}
    _lines   : dict[str, QLineF] = {}
    _paths   : dict[str, dict[Direction, QPainterPath]] = {}

    def __init__(self : Self) -> None:
        self.update()
        settings().changed.connect(self.update)

    def update(self : Self) -> None:
        # pens
        for item_name in self._PEN_ITEMS:
            pen_normal, pen_selected = self._getPens(
                f"theme/items/{item_name}/line"
            )
            self._pens[item_name] = {
                False : pen_normal,
                True : pen_selected
            }
        # brushes
        for item_name in self._BRUSH_ITEMS:
            brush_normal, brush_selected = self._getBrushes(
                f"theme/items/{item_name}/fill"
            )
            self._brushes[item_name] = {
                False : brush_normal,
                True : brush_selected
            }
        # quills
        self._quills = {}
        for item_name in self._QUILL_ITEMS:
            self._loadQuill(item_name)
        # grip pens, brushes and paths
        self._pens["Grip"] = self._getPen("theme/grip/line")
        self._brushes["Grip"] = self._getBrush("theme/grip/fill")
        self._paths["Grip"] = {}
        size = settings().get("theme/grip/size")
        rect = QRectF(-size/2, -size/2, size, size)
        square = QPainterPath()
        square.addRect(rect)
        self._paths["Grip"][GripShape.SQUARE] = square
        circle = QPainterPath()
        circle.addEllipse(rect)
        self._paths["Grip"][GripShape.CIRCLE] = circle
        diamond = QPainterPath()
        diamond.addPolygon(QPolygonF([
            QPointF(-size/2, 0),
            QPointF(0, -size/2),
            QPointF(size/2, 0),
            QPointF(0, size/2)
        ]))
        self._paths["Grip"][GripShape.DIAMOND] = diamond
        arrow = QPainterPath()
        arrow.addPolygon(QPolygonF([
            QPointF(-size/2, -size/2),
            QPointF(size/2, 0),
            QPointF(-size/2, size/2)
        ]))
        self._paths["Grip"][GripShape.ARROW] = arrow
        star = QPainterPath()
        star.addRect(rect)
        rotated = QPainterPath()
        rotated.addRect(rect)
        rotated = QTransform().rotate(45).map(rotated)
        star = star.united(rotated)
        self._paths["Grip"][GripShape.STAR] = star
        # tether pen
        self._pens["Tether"] = self._getPen("theme/tether/line")
        # pin pens
        pin_items = self._PIN_PATH_ITEMS + list(self._PIN_LINE_ITEMS.keys())
        for item_name in pin_items:
            self._pens[item_name] = {}
            for bus in [False, True]:
                wire_bus = "bus" if bus else "wire"
                pen_normal, pen_selected = self._getPens(
                    f"theme/items/{item_name}/pin/{wire_bus}/line"
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
                    f"{settings_path}/arrow/line",
                    cap_style=Qt.PenCapStyle.FlatCap
                )
            pen_selected = QPen(pen_normal)
            pen_selected.setColor(settings().get("theme/selected/line"))
            self._pens[item_name] = {
                False : pen_normal,
                True  : pen_selected
            }
            brush_normal, brush_selected = \
                self._getBrushes(f"{settings_path}/arrow/fill")
            self._brushes[item_name] = {
                False : brush_normal,
                True : brush_selected
            }

    def pen(
        self      : Self,
        item_name : str,
        key       : bool | tuple | None = None
    ) -> QPen:
        if item_name not in self._pens:
            raise ValueError(f"No pen defined for item {item_name}")
        return self._pens[item_name] if key is None \
            else self._pens[item_name][key]

    def brush(
        self      : Self,
        item_name : str,
        key       : bool | tuple | None = None
    ) -> QBrush:
        if item_name not in self._brushes:
            raise ValueError(f"No brush defined for item {item_name}")
        return self._brushes[item_name] if key is None \
            else self._brushes[item_name][key]

    def quill(
        self      : Self,
        item_name : str,
        key       : bool | tuple | None = None
    ) -> Quill:
        if item_name not in self._quills:
            self._loadQuill(item_name)
        return self._quills[item_name] if key is None \
            else self._quills[item_name][key]

    def _loadQuill(self : Self, item_name : str) -> None:
        try:
            quill_normal, quill_selected = self._getQuills(
                f"theme/items/{item_name}/text"
            )
        except KeyError:
            raise ValueError(f"No quill defined for item {item_name}") from None
        self._quills[item_name] = {
            False : quill_normal,
            True  : quill_selected
        }

    def line(self : Self, item_name : str) -> QLineF:
        if item_name not in self._lines:
            raise ValueError(f"No line defined for item {item_name}")
        return self._lines[item_name]

    def path(self : Self, item_name : str, key : Direction) -> QPainterPath:
        if item_name not in self._paths:
            raise ValueError(f"No path defined for item {item_name}")
        return self._paths[item_name][key]

    def _getPen(
        self          : Self,
        settings_path : str,
        cap_style     : Qt.PenCapStyle = Qt.PenCapStyle.FlatCap,
        join_style    : Qt.PenJoinStyle = Qt.PenJoinStyle.MiterJoin
    ) -> QPen:
        return QPen(
            settings().get(f"{settings_path}/color"),
            settings().get(f"{settings_path}/width"),
            settings().get(f"{settings_path}/style"),
            cap_style,
            join_style
        )

    def _getPens(
        self          : Self,
        settings_path : str,
        cap_style     : Qt.PenCapStyle = Qt.PenCapStyle.FlatCap,
        join_style    : Qt.PenJoinStyle = Qt.PenJoinStyle.MiterJoin
    ) -> tuple[QPen, QPen]:
        pen_normal = self._getPen(settings_path, cap_style, join_style)
        pen_selected = QPen(pen_normal)
        pen_selected.setColor(settings().get("theme/selected/line"))
        return pen_normal, pen_selected

    def _getBrush(self : Self, settings_path : str) -> QBrush:
        return QBrush(
            settings().get(f"{settings_path}/color"),
            settings().get(f"{settings_path}/style")
        )

    def _getBrushes(self : Self, settings_path : str) -> tuple[QBrush, QBrush]:
        brush_normal = self._getBrush(settings_path)
        brush_selected = QBrush(brush_normal)
        brush_selected.setColor(settings().get("theme/selected/fill"))
        return brush_normal, brush_selected

    def _getQuill(self : Self, settings_path : str) -> Quill:
        return Quill(
            settings().get(f"{settings_path}/color"),
            settings().get(f"{settings_path}/font"),
            settings().get(f"{settings_path}/size"),
            settings().get(f"{settings_path}/bold"),
            settings().get(f"{settings_path}/italic"),
            settings().get(f"{settings_path}/underline")
        )

    def _getQuills(self : Self, settings_path : str) -> tuple[Quill, Quill]:
        quill_normal = self._getQuill(settings_path)
        quill_selected = Quill(quill_normal)
        quill_selected.setColor(settings().get("theme/selected/text"))
        return quill_normal, quill_selected

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
