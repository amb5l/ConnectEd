from typing import Self

from PyQt6.QtCore import Qt, QLineF, QRectF
from PyQt6.QtGui  import QPainterPath, QPen

from .....app import settings

from .....core.defs  import PITCH
from .....core.types import NetKind

from ...items.node import NodeState

from ..drawing.resources import DrawingSceneResources


class DiagramSceneResources(DrawingSceneResources):
    _PEN_ITEMS = DrawingSceneResources._PEN_ITEMS + ["Gate"]
    _BRUSH_ITEMS = DrawingSceneResources._BRUSH_ITEMS + ["Gate"]
    _QUILL_ITEMS = DrawingSceneResources._QUILL_ITEMS + ["NetLabel"]
    _PIN_PATH_ITEMS = DrawingSceneResources._PIN_PATH_ITEMS + ["GatePin"]
    _PIN_LINE_ITEMS = {"Port" : PITCH, "BlockPin" : -PITCH}
    _PIN_ARROW_ITEMS = DrawingSceneResources._PIN_ARROW_ITEMS | \
        {
            "PortArrow"     : (True, True),
            "BlockPinArrow" : (True, False),
            "GatePinArrow"  : (False, False),
        }
    _NODE_ITEMS = ["FreeNode", "FixedNode"]

    def update(self : Self):
        """Typically called after a settings change."""
        # DrawingSceneResources
        super().update()
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
