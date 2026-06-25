from typing import Self

from PyQt6.QtCore import Qt, QLineF, QRectF
from PyQt6.QtGui  import QPainterPath, QPen, QBrush

from .....app import settings

from .....core.defs  import PITCH, WIDTH
from .....core.types import NetKind, Direction

from ...items.node import NodeState

from ..drawing.resources import DrawingSceneResources


class DiagramSceneResources(DrawingSceneResources):
    _PEN_ITEMS = \
        DrawingSceneResources._PEN_ITEMS + ["Gate"]
    _BRUSH_ITEMS = \
        DrawingSceneResources._BRUSH_ITEMS + ["Gate"]
    _QUILL_ITEMS = \
        DrawingSceneResources._QUILL_ITEMS + ["PropertyText", "NetLabel"]
    _PIN_PATH_ITEMS = ["SymbolPin", "GatePin"]
    _PIN_LINE_ITEMS = {"Port" : PITCH, "BlockPin" : -PITCH}
    _PIN_ARROW_ITEMS = {
        "SymbolPinArrow" : ( False , False ),  # : internal, input faces left
        "BlockPinArrow"  : ( True  , False ),
        "GatePinArrow"   : ( False , False ),
        "PortArrow"      : ( True  , True  )
    }
    _NODE_ITEMS = ["FreeNode", "FixedNode"]

    def update(self : Self):
        """Typically called after a settings change."""
        # DrawingSceneResources
        super().update()
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
            self._pens[item_name] = {}
            for bus in [False, True]:
                wire_bus = "bus" if bus else "wire"
                pen_normal, pen_selected = self._getPens(
                    item_name, f"theme/items/{item_name}/pin/{wire_bus}/line"
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
            for state in NodeState:
                state_str = state.value
                # pens
                pen_normal, pen_selected = \
                    self._getPens(
                        item_name,
                        f"{settings_path}/{state_str}/line",
                    )
                self._pens[item_name][(state, False)] = pen_normal
                self._pens[item_name][(state, True)] = pen_selected
                # brushes
                brush_normal, brush_selected = \
                    self._getBrushes(
                        item_name,
                        f"{settings_path}/{state_str}/fill",
                    )
                self._brushes[item_name][(state, False)] = brush_normal
                self._brushes[item_name][(state, True)] = brush_selected
                # paths
                self._paths[item_name][state] = self._nodePath(state, size)
        # GateRound
        self._pens["GateRound"] = {}
        self._brushes["GateRound"] = {}
        for selected in [False, True]:
            pen = QPen(self._pens["Gate"][selected])
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            self._pens["GateRound"][selected] = pen
            brush = self._brushes["Gate"][selected]
            self._brushes["GateRound"][selected] = brush
        # BufGatePinItem and OrGatePinItem
        for item_name in ["BufGatePin", "OrGatePin"]:
            self._pens[item_name] = {}
            extend = 2 if item_name == "BufGatePin" else 4
            for bus in [False, True]:
                for selected in [False, True]:
                    self._pens[item_name][(bus, selected)] = \
                        self._pens["GatePin"][(bus, selected)]
            self._paths[item_name] = {}
            for key, path in self._paths["GatePin"].items():
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
