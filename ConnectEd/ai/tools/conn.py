"""AI tools for diagram connectivity."""

from typing import Any

from PyQt6.QtCore import QPointF

from ...core.check import checked

from ..refs import RefRegistry

from .params import _VIEW_PARAM
from .utils  import aitool, toolError, toolOk
from .private import _drawingSceneFromViewRef

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...widgets.graphics.scenes.diagram import DiagramScene
    from ...widgets.window import Window

################################################################################

_OFFSET_PROPS = {
    "axis"  : {
        "type"        : "string",
        "description" : "Leg direction: H (horizontal) or V (vertical).",
    },
    "delta" : {
        "type"        : "number",
        "description" : "Signed length along that axis in scene units.",
    },
}

_START_PROPS = {
    "start" : {
        "type"        : "object",
        "description" : "Start point in scene coordinates (use instead of start_ref).",
        "properties"  : {
            "x" : {"type": "number", "description": "Scene X."},
            "y" : {"type": "number", "description": "Scene Y."},
        },
        "required"    : ["x", "y"],
    },
    "start_ref" : {
        "type"        : "string",
        "description" : (
            "Item ref (port, block pin, or tap) whose connection node is the start "
            "point (from get_items / add_block_pin)."
        ),
    },
}

################################################################################

@aitool(
    description = (
        "Add orthogonal connection segments from a start point through a list of "
        "horizontal (H) or vertical (V) offsets. Prefer grid multiples of 10."
    ),
    parameters  = {
        "type"       : "object",
        "properties" : {
            **_VIEW_PARAM["properties"],
            **_START_PROPS,
            "offsets" : {
                "type"        : "array",
                "description" : (
                    "Routing legs in order; each moves along one axis only."
                ),
                "items"       : {
                    "type"       : "object",
                    "properties" : _OFFSET_PROPS,
                    "required"   : ["axis", "delta"],
                },
            },
        },
        "required"   : ["view", "offsets"],
    },
    write = True,
)
@checked
def add_connection(
    window    : "Window",
    registry  : RefRegistry,
    arguments : dict[str, Any],
) -> str:
    offsets_in = arguments.get("offsets")
    if not isinstance(offsets_in, list) or not offsets_in:
        return toolError("offsets must be a non-empty array")

    legs : list[tuple[str, float]] = []
    for index, leg_in in enumerate(offsets_in):
        leg, err = _parseOffsetLeg(leg_in, index)
        if err is not None:
            return err
        legs.append(leg)

    start, err = _resolveStart(registry, arguments)
    if err is not None:
        return err

    scene, err = _drawingSceneFromViewRef(registry, arguments["view"])
    if scene is None:
        return toolError(err or "Invalid view")

    end = _routeConnection(scene, start, legs)
    scene.netlistChanged.emit()
    return toolOk(
        end_x = end.x(),
        end_y = end.y(),
        legs  = len(legs),
    )

################################################################################

def _parseOffsetLeg(
    leg_in : Any,
    index  : int,
) -> tuple[tuple[str, float] | None, str | None]:
    if not isinstance(leg_in, dict):
        return None, toolError(f"offsets[{index}] must be an object")
    axis_raw = leg_in.get("axis")
    if not isinstance(axis_raw, str) or not axis_raw.strip():
        return None, toolError(f"offsets[{index}].axis is required")
    axis = axis_raw.strip().upper()
    if axis not in ("H", "V"):
        return None, toolError(f"offsets[{index}].axis must be H or V")
    delta = leg_in.get("delta")
    if not isinstance(delta, (int, float)) or isinstance(delta, bool):
        return None, toolError(f"offsets[{index}].delta is required")
    delta_f = float(delta)
    if delta_f == 0.0:
        return None, toolError(f"offsets[{index}].delta must be non-zero")
    return (axis, delta_f), None


def _resolveStart(
    registry  : RefRegistry,
    arguments : dict[str, Any],
) -> tuple[QPointF | None, str | None]:
    start_ref = arguments.get("start_ref")
    start     = arguments.get("start")
    has_ref   = isinstance(start_ref, str) and bool(start_ref.strip())
    has_start = isinstance(start, dict)
    if has_ref and has_start:
        return None, toolError("Provide start or start_ref, not both")
    if has_ref:
        return _startFromItemRef(registry, start_ref.strip())
    if has_start:
        x = start.get("x")
        y = start.get("y")
        if not isinstance(x, (int, float)) or isinstance(x, bool):
            return None, toolError("start.x is required")
        if not isinstance(y, (int, float)) or isinstance(y, bool):
            return None, toolError("start.y is required")
        return QPointF(float(x), float(y)), None
    return None, toolError("start or start_ref is required")


def _startFromItemRef(
    registry  : RefRegistry,
    start_ref : str,
) -> tuple[QPointF | None, str | None]:
    item = registry.resolve(start_ref, kind="item")
    if item is None:
        return None, toolError(f"Unknown or stale item ref: {start_ref!r}")

    from ...widgets.graphics.items.port_pin import PortPinMixin
    if isinstance(item, PortPinMixin):
        return item._node.scenePos(), None

    from ...widgets.graphics.items.tap import TapItem
    if isinstance(item, TapItem):
        return item.majorNode().scenePos(), None

    return None, toolError(
        "start_ref must be a port, block pin, or tap (not a block or segment)",
    )


@checked
def _routeConnection(
    scene : "DiagramScene",
    start : QPointF,
    legs  : list[tuple[str, float]],
) -> QPointF:
    scene.undo_stack.beginMacro("addConnection")
    try:
        pos  = QPointF(start)
        prev = QPointF(start)
        for axis, delta in legs:
            if axis == "H":
                pos = QPointF(pos.x() + delta, pos.y())
            else:
                pos = QPointF(pos.x(), pos.y() + delta)
            scene.addSegment(prev, pos, undoable=True)
            prev = QPointF(pos)
    finally:
        scene.undo_stack.endMacro()
    return pos
