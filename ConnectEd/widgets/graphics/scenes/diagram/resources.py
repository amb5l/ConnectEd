from typing import Self, Any, TypeAlias

from PyQt6.QtCore import Qt, QPointF, QLineF, QRectF
from PyQt6.QtGui  import QPolygonF, QTransform, QPainterPath, QColor, QPen, QBrush

from .....app import settings

from .....core.check import checked
from .....core.defs  import PITCH, WIDTH
from .....core.types import NetKind, Direction

from ...quill import Quill

from ...items.grip import GripShape
from ...items.node import NodeState


PenTable : TypeAlias = dict[Any, QPen]
BrushTable : TypeAlias = dict[Any, QBrush]
QuillTable : TypeAlias = dict[Any, Quill]


class DiagramSceneResources:
    # class attributes
    _PEN_ITEMS   = ["Rectangle", "Ellipse", "Block", "Line", "Polyline", "Gate"]
    _BRUSH_ITEMS = ["Rectangle", "Ellipse", "Block", "Polyline", "Gate"]
    _QUILL_ITEMS = ["Text", "PropertyText", "NetLabel"]
    _PIN_PATH_ITEMS = ["SymbolPin", "GatePin"]
    _PIN_LINE_ITEMS = {"Port" : PITCH, "BlockPin" : -PITCH}
    _PIN_ARROW_ITEMS = {
        "SymbolPinArrow" : ( False , False ),  # : internal, input faces left
        "BlockPinArrow"  : ( True  , False ),
        "GatePinArrow"   : ( False , False ),
        "PortArrow"      : ( True  , True  )
    }
    _NODE_ITEMS = ["FreeNode", "FixedNode"]

    # instance attributes
    _pens    : dict[str, QPen | PenTable]
    _brushes : dict[str, QBrush | BrushTable]
    _quills  : dict[str, Quill | QuillTable]
    _lines   : dict[str, QLineF]
    _paths   : dict[str, dict[Any, QPainterPath]]

    @checked
    def __init__(self : Self) -> None:
        self._pens = {}
        self._brushes = {}
        self._quills = {}
        self._lines = {}
        self._paths = {}
        self.update()
        settings().changed.connect(self.update)

    def update(self : Self):
        """Typically called after a settings change."""
        # pens
        for item_name in self._PEN_ITEMS:
            pen_normal, pen_selected = self._getPens(
                item_name,
                f"theme/items/{item_name}/line",
            )
            self._pens[item_name] = {
                False : pen_normal,
                True : pen_selected
            }
        # brushes
        self._brushes = {}
        for item_name in self._BRUSH_ITEMS:
            brush_normal, brush_selected = self._getBrushes(
                item_name,
                f"theme/items/{item_name}/fill",
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


        # symbol body
        self._pens["Symbol"] = {}
        pen_normal, pen_selected = self._getPens(
            "Symbol", "theme/items/SymbolBody/line"
        )
        pen_none = QPen(pen_normal)
        pen_none.setStyle(Qt.PenStyle.NoPen)
        self._pens["Symbol"][(False, False)] = pen_none
        self._pens["Symbol"][(False, True)] = pen_selected
        self._pens["Symbol"][(True, False)] = pen_normal
        self._pens["Symbol"][(True, True)] = pen_selected
        self._brushes["Symbol"] = {}
        brush_normal, brush_selected = self._getBrushes(
            "Symbol", "theme/items/SymbolBody/fill"
        )
        brush_none = QBrush(brush_normal)
        brush_none.setStyle(Qt.BrushStyle.NoBrush)
        self._brushes["Symbol"][(False, False)] = brush_none
        self._brushes["Symbol"][(False, True)] = brush_selected
        self._brushes["Symbol"][(True, False)] = brush_normal
        self._brushes["Symbol"][(True, True)] = brush_selected
        # tether pen
        self._pens["Tether"] = self._getPen("theme/tether/line")
        # pin pens
        pin_items = self._PIN_PATH_ITEMS + list(self._PIN_LINE_ITEMS.keys())
        for item_name in pin_items:
            pin_pens : dict[Any, QPen] = {}
            for bus in [False, True]:
                wire_bus = "bus" if bus else "wire"
                pen_normal, pen_selected = self._getPens(
                    item_name, f"theme/items/{item_name}/pin/{wire_bus}/line"
                )
                pin_pens[(bus, False)] = pen_normal
                pin_pens[(bus, True)]  = pen_selected
            self._pens[item_name] = pin_pens
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
                    path = self._extArrowPath(size, arrow_dir[direction])
                self._paths[item_name][direction] = path
            pen_normal, pen_selected = \
                self._getPens(
                    pin_item_name,
                    f"{settings_path}/arrow/line",
                    cap_style=Qt.PenCapStyle.FlatCap,
                )
            self._pens[item_name] = {
                False : pen_normal,
                True  : pen_selected
            }
            brush_normal, brush_selected = \
                self._getBrushes(
                    pin_item_name,
                    f"{settings_path}/arrow/fill",
                )
            self._brushes[item_name] = {
                False : brush_normal,
                True : brush_selected
            }
        # node pens, brushes and paths
        for item_name in self._NODE_ITEMS:
            settings_path = f"theme/items/{item_name}"
            self._pens[item_name] = {}
            self._brushes[item_name] = {}
            self._paths[item_name] = {}
            size = settings().get(f"{settings_path}/size")
            item_pens : dict[tuple[NodeState, bool], QPen] = {}
            item_brushes : dict[tuple[NodeState, bool], QBrush] = {}
            for state in NodeState:
                state_str = state.value
                # pens
                pen_normal, pen_selected = \
                    self._getPens(
                        item_name,
                        f"{settings_path}/{state_str}/line",
                    )
                item_pens[(state, False)] = pen_normal
                item_pens[(state, True)]  = pen_selected
                # brushes
                brush_normal, brush_selected = \
                    self._getBrushes(
                        item_name,
                        f"{settings_path}/{state_str}/fill",
                    )
                item_brushes[(state, False)] = brush_normal
                item_brushes[(state, True)]  = brush_selected
                # paths
                self._paths[item_name][state] = self._nodePath(state, size)
            self._pens[item_name] = item_pens
            self._brushes[item_name] = item_brushes
        # GateRound
        self._pens["GateRound"] = {}
        self._brushes["GateRound"] = {}
        for selected in [False, True]:
            gate_pens = self._pens["Gate"]
            if not isinstance(gate_pens, dict):
                raise TypeError("Bad gate pens")
            gate_pen = QPen(gate_pens[selected])
            gate_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            gate_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            self._pens["GateRound"][selected] = gate_pen
            gate_brushes = self._brushes["Gate"]
            if not isinstance(gate_brushes, dict):
                raise TypeError("Bad gate brushes")
            gate_brush = QBrush(gate_brushes[selected])
            self._brushes["GateRound"][selected] = gate_brush
        # BufGatePinItem and OrGatePinItem
        for item_name in ["BufGatePin", "OrGatePin"]:
            self._pens[item_name] = {}
            extend = 2 if item_name == "BufGatePin" else 4
            for bus in [False, True]:
                for selected in [False, True]:
                    gate_pins = self._pens["GatePin"]
                    if not isinstance(gate_pins, dict):
                        raise TypeError("Bad gate pins")
                    gate_pin = gate_pins[(bus, selected)]
                    buf_or_gate_pins = self._pens[item_name]
                    if not isinstance(buf_or_gate_pins, dict):
                        raise TypeError("Bad buf or gate pins")
                    buf_or_gate_pins[(bus, selected)] = gate_pin
            self._paths[item_name] = {}
            gate_pin_paths = self._paths["GatePin"]
            if not isinstance(gate_pin_paths, dict):
                raise TypeError("Bad gate pin paths")
            for key, path in gate_pin_paths.items():
                path = QPainterPath(path)  # copy before modifying
                path.setElementPositionAt(0, path.elementAt(0).x - extend, 0)
                self._paths[item_name][key] = path
        # tap pen and line
        settings_path = "theme/items/Tap"
        self._pens["Tap"] = {}
        for kind in NetKind:
            pen_normal, pen_selected = self._getPens(
                "Tap",
                f"{settings_path}/line/{kind.value}",
            )
            self._pens["Tap"][(kind, False)] = pen_normal
            self._pens["Tap"][(kind, True)]  = pen_selected
        self._lines["Tap"] = QLineF(0, 0, PITCH, PITCH)
        # Segment
        self._pens["Segment"] = {}
        for kind in NetKind:
            settings_path = f"theme/items/Segment/line/{kind.value}"
            pen_normal, pen_selected = self._getPens(
                "Segment",
                settings_path,
                cap_style=Qt.PenCapStyle.RoundCap,
            )
            self._pens["Segment"][(kind, False)] = pen_normal
            self._pens["Segment"][(kind, True)]  = pen_selected
        # SegmentPreview1 and SegmentPreview2
        self._pens["SegmentPreview1"] = self._getPen(
            "theme/items/SegmentPreview1/line", Qt.PenCapStyle.RoundCap
        )
        self._pens["SegmentPreview2"] = self._getPen(
            "theme/items/SegmentPreview2/line", Qt.PenCapStyle.RoundCap
        )
        # rubber pen
        self._pens["rubber"] = self._getPen(
            "theme/rubber/line", Qt.PenCapStyle.RoundCap
        )

    def pen(
        self      : Self,
        item_name : str,
        key       : bool | tuple | None = None
    ) -> QPen:
        if item_name not in self._pens:
            raise ValueError(f"No pen defined for item {item_name}")
        entry = self._pens[item_name]
        if key is None:
            if isinstance(entry, dict):
                raise TypeError(f"Pen table for {item_name} requires a key")
            return entry
        if not isinstance(entry, dict):
            raise TypeError(f"Pen for {item_name} is not a table")
        return entry[key]

    def brush(
        self      : Self,
        item_name : str,
        key       : bool | tuple | None = None
    ) -> QBrush:
        if item_name not in self._brushes:
            raise ValueError(f"No brush defined for item {item_name}")
        entry = self._brushes[item_name]
        if key is None:
            if isinstance(entry, dict):
                raise TypeError(f"Brush table for {item_name} requires a key")
            return entry
        if not isinstance(entry, dict):
            raise TypeError(f"Brush for {item_name} is not a table")
        return entry[key]

    def quill(
        self      : Self,
        item_name : str,
        key       : bool | tuple | None = None
    ) -> Quill:
        if item_name not in self._quills:
            self._loadQuill(item_name)
        entry = self._quills[item_name]
        if key is None:
            if isinstance(entry, dict):
                raise TypeError(f"Quill table for {item_name} requires a key")
            return entry
        if not isinstance(entry, dict):
            raise TypeError(f"Quill for {item_name} is not a table")
        return entry[key]

    def _loadQuill(self : Self, item_name : str) -> None:
        try:
            quill_normal, quill_selected = self._getQuills(
                item_name,
                f"theme/items/{item_name}/text",
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

    def path(self : Self, item_name : str, key : Any) -> QPainterPath:
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

    def _selectedColor(self : Self, part : str) -> QColor:
        spec = settings().get(f"theme/selected/{part}")
        if hasattr(spec, "color"):
            return spec.color
        return spec

    def _selectedItemPart(
        self      : Self,
        item_name : str,
        part      : str,
    ) -> Any | None:
        try:
            items = settings().get("theme/selected/items")
        except KeyError:
            return None
        if not hasattr(items, item_name):
            return None
        block = getattr(items, item_name)
        if not hasattr(block, part):
            return None
        return getattr(block, part)

    def _applySelectedLine(
        self      : Self,
        item_name : str,
        pen       : QPen,
    ) -> QPen:
        pen_sel = QPen(pen)
        spec = settings().get("theme/selected/line")
        if hasattr(spec, "color"):
            pen_sel.setColor(spec.color)
        else:
            pen_sel.setColor(spec)
        if hasattr(spec, "width"):
            pen_sel.setWidthF(float(spec.width))
        if hasattr(spec, "style"):
            pen_sel.setStyle(spec.style)
        override = self._selectedItemPart(item_name, "line")
        if override is not None:
            if hasattr(override, "color"):
                pen_sel.setColor(override.color)
            if hasattr(override, "width"):
                pen_sel.setWidthF(float(override.width))
            if hasattr(override, "style"):
                pen_sel.setStyle(override.style)
        return pen_sel

    def _applySelectedBrush(
        self      : Self,
        item_name : str,
        brush     : QBrush,
    ) -> QBrush:
        brush_sel = QBrush(brush)
        spec = settings().get("theme/selected/fill")
        if hasattr(spec, "color"):
            brush_sel.setColor(spec.color)
        else:
            brush_sel.setColor(spec)
        if hasattr(spec, "style"):
            brush_sel.setStyle(spec.style)
        override = self._selectedItemPart(item_name, "fill")
        if override is not None:
            if hasattr(override, "color"):
                brush_sel.setColor(override.color)
            if hasattr(override, "style"):
                brush_sel.setStyle(override.style)
        return brush_sel

    def _applySelectedQuill(
        self      : Self,
        item_name : str,
        quill     : Quill,
    ) -> Quill:
        quill_sel = Quill(quill)
        spec = settings().get("theme/selected/text")
        if hasattr(spec, "color"):
            quill_sel.setColor(spec.color)
        else:
            quill_sel.setColor(spec)
        for attr in ("font", "size", "bold", "italic", "underline"):
            if hasattr(spec, attr):
                setter = getattr(quill_sel, f"set{attr.capitalize()}")
                setter(getattr(spec, attr))
        override = self._selectedItemPart(item_name, "text")
        if override is not None:
            if hasattr(override, "color"):
                quill_sel.setColor(override.color)
            for attr in ("font", "size", "bold", "italic", "underline"):
                if hasattr(override, attr):
                    setter = getattr(quill_sel, f"set{attr.capitalize()}")
                    setter(getattr(override, attr))
        return quill_sel

    def _getPens(
        self          : Self,
        item_name     : str,
        settings_path : str,
        cap_style     : Qt.PenCapStyle = Qt.PenCapStyle.FlatCap,
        join_style    : Qt.PenJoinStyle = Qt.PenJoinStyle.MiterJoin
    ) -> tuple[QPen, QPen]:
        pen_normal = self._getPen(settings_path, cap_style, join_style)
        pen_selected = self._applySelectedLine(item_name, pen_normal)
        return pen_normal, pen_selected

    def _getBrush(self : Self, settings_path : str) -> QBrush:
        return QBrush(
            settings().get(f"{settings_path}/color"),
            settings().get(f"{settings_path}/style")
        )

    def _getBrushes(
        self          : Self,
        item_name     : str,
        settings_path : str,
    ) -> tuple[QBrush, QBrush]:
        brush_normal = self._getBrush(settings_path)
        brush_selected = self._applySelectedBrush(item_name, brush_normal)
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

    def _getQuills(
        self          : Self,
        item_name     : str,
        settings_path : str,
    ) -> tuple[Quill, Quill]:
        quill_normal = self._getQuill(settings_path)
        quill_selected = self._applySelectedQuill(item_name, quill_normal)
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

    def _nodePath(self : Self, state : NodeState, size : float) -> QPainterPath:
        path = QPainterPath()
        match state:
            case NodeState.UNCONNECTED:
                # square
                path.addRect(QRectF(-size/2, -size/2, size, size))
            case NodeState.CONNECTED:
                # diamond
                path.moveTo(-size/2, 0)
                path.lineTo(0, -size/2)
                path.lineTo(size/2, 0)
                path.lineTo(0, size/2)
                path.closeSubpath()
            case NodeState.JUNCTION:
                # circle
                path.addEllipse(QRectF(-size/2, -size/2, size, size))
            case _:
                raise ValueError(f"Invalid node state: {state}")
        return path
