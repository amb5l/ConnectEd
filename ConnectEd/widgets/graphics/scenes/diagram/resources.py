from typing import Self

from PyQt6.QtCore import QLineF, QRectF
from PyQt6.QtGui  import QPainterPath, QPen

from .....app import settings

from .....core.defs import PITCH

from ...items.node import NodeState

from ..drawing.resources import DrawingSceneResources, DrawingSceneResourcesMixin


class DiagramSceneResources(DrawingSceneResources):
    _PIN_PATH_ITEMS = DrawingSceneResources._PIN_PATH_ITEMS + ["GatePin"]
    _PIN_LINE_ITEMS = {"Port" : PITCH, "BlockPin" : -PITCH}
    _PIN_ARROW_ITEMS = DrawingSceneResources._PIN_ARROW_ITEMS | \
        {
            "PortArrow"     : (True, True),
            "BlockPinArrow" : (True, False),
            "GatePinArrow"  : (False, False),
        }
    _NODE_ITEMS = ["FreeNode", "FixedNode"]

    def __init__(self : Self):
        self.update()
        settings().changed.connect(self.update)

    def update(self : Self):
        """Typically called after a settings change."""
        # DrawingSceneResources
        super().update()
        # BufGatePinItem and OrGatePinItem
        for item_name in ["BufGatePin", "OrGatePin"]:
            self._pens[item_name] = {}
            offset = 2 if item_name == "BufGatePin" else 4
            for bus in [False, True]:
                for selected in [False, True]:
                    self._pens[item_name][(bus, selected)] = \
                        QPen(self._pens["GatePin"][(bus, selected)])
            self._paths[item_name] = {}
            for key, path in self._paths["GatePin"].items():
                path = QPainterPath(path)
                path.setElementPositionAt(0, path.elementAt(0).x - offset, 0)
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
                    self._getPens(f"{settings_path}/{state_str}/pen")
                self._pens[item_name][(state, False)] = pen_normal
                self._pens[item_name][(state, True)] = pen_selected
                # brushes
                brush_normal, brush_selected = \
                    self._getBrushes(f"{settings_path}/{state_str}/brush")
                self._brushes[item_name][(state, False)] = brush_normal
                self._brushes[item_name][(state, True)] = brush_selected
                # paths
                self._paths[item_name][state] = self._nodePath(state, size)
        # tap pen and line
        settings_path = "theme/items/Tap"
        self._pens["Tap"] = {}
        self._pens["Tap"][False] = self._getPens(f"{settings_path}/pen/wire")
        self._pens["Tap"][True] = self._getPens(f"{settings_path}/pen/bus")
        self._lines["Tap"] = QLineF(0, 0, PITCH, PITCH)

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


class DiagramSceneResourcesMixin(DrawingSceneResourcesMixin):
    pass
