from __future__ import annotations

from typing import Any

from ...core.check import checked
from ...core.types import Direction, Edge

from ..refs   import RefRegistry
from .utils   import aitool, toolError, toolOk
from .private import _drawingSceneFromViewRef

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...widgets.graphics.items.block import BlockItem
    from ...widgets.graphics.scenes.diagram import DiagramScene
    from ...widgets.window import Window

################################################################################

_PIN_SPEC_PROPS = {
    "name"      : {
        "type"        : "string",
        "description" : "Pin name e.g. clk or data[7:0] (bus if name contains ':').",
    },
    "direction" : {
        "type"        : "string",
        "description" : "Pin direction: in, out, or bi (VHDL inout maps to bi).",
    },
    "edge"      : {
        "type"        : "string",
        "description" : "Block edge: left, right, top, or bottom.",
    },
    "offset"    : {
        "type"        : "number",
        "description" : "Distance along the edge from its left or top end.",
    },
}

_BLOCK_PIN_VIEW_ITEM = {
    "view" : {
        "type"        : "string",
        "description" : "Diagram view reference from get_active_view.",
    },
    "item" : {
        "type"        : "string",
        "description" : "Block item reference from add_block or get_items.",
    },
}

################################################################################

@aitool(
    description = "Add pin to specified block.",
    parameters  = {
        "type"       : "object",
        "properties" : {
            **_BLOCK_PIN_VIEW_ITEM,
            **_PIN_SPEC_PROPS,
        },
        "required"   : ["view", "item", "name", "direction", "edge", "offset"],
    },
    write = True,
)
@checked
def add_block_pin(
    window    : Window,
    registry  : RefRegistry,
    arguments : dict[str, Any],
) -> str:
    spec, err = _parsePinSpec(arguments)
    if err is not None:
        return err
    block, err = _resolveBlock(registry, arguments["item"])
    if err is not None:
        return err
    scene, err = _drawingSceneFromViewRef(registry, arguments["view"])
    if scene is None:
        return toolError(err or "Invalid view")
    pin, err = _placeBlockPin(scene, block, spec)
    if err is not None:
        return err
    return toolOk(ref=registry.issue("item", pin))

################################################################################

@aitool(
    description = "Edit properties of specified pin.",
    parameters  = {
        "type"       : "object",
        "properties" : {
            **_BLOCK_PIN_VIEW_ITEM,
            **_PIN_SPEC_PROPS,
        },
        "required"   : ["view", "item"],
    },
    write = True,
)
@checked
def edit_block_pin(
    window    : Window,
    registry  : RefRegistry,
    arguments : dict[str, Any]
):
    spec, err = _parsePinSpec(arguments)
    if err is not None:
        return err
    block, err = _resolveBlock(registry, arguments["item"])
    if err is not None:
        return err
    scene, err = _drawingSceneFromViewRef(registry, arguments["view"])
    if scene is None:
        return toolError(err or "Invalid view")
    pin, err = _placeBlockPin(scene, block, spec)
    if err is not None:
        return err
    return toolOk(ref=registry.issue("item", pin))

################################################################################

@aitool(
    description = (
        "Add multiple pins to a specified block."
    ),
    parameters  = {
        "type"       : "object",
        "properties" : {
            **_BLOCK_PIN_VIEW_ITEM,
            "pins" : {
                "type"        : "array",
                "description" : "Pin definitions (name, direction, edge, offset).",
                "items"       : {
                    "type"       : "object",
                    "properties" : _PIN_SPEC_PROPS,
                    "required"   : ["name", "direction", "edge", "offset"],
                },
            },
        },
        "required"   : ["view", "item", "pins"],
    },
    write = True,
)
@checked
def add_block_pins(
    window    : Window,
    registry  : RefRegistry,
    arguments : dict[str, Any],
) -> str:
    pins_in = arguments.get("pins")
    if not isinstance(pins_in, list) or not pins_in:
        return toolError("pins must be a non-empty array")
    parsed : list[dict[str, Any]] = []
    for spec_in in pins_in:
        spec, err = _parsePinSpec(spec_in)
        if err is not None:
            return err
        parsed.append(spec)
    block, err = _resolveBlock(registry, arguments["item"])
    if err is not None:
        return err
    scene, err = _drawingSceneFromViewRef(registry, arguments["view"])
    if scene is None:
        return toolError(err or "Invalid view")
    placed : list[dict[str, str]] = []
    for spec in parsed:
        pin, place_err = _placeBlockPin(scene, block, spec)
        if place_err is not None:
            return place_err
        placed.append({
            "ref"  : registry.issue("item", pin),
            "name" : spec["name"],
        })
    return toolOk(pins=placed)

################################################################################

def _edgeFromTool(edge : str) -> Edge | None:
    key = edge.strip().upper()
    return Edge[key] if key in Edge.__members__ else None


def _directionFromTool(direction : str) -> Direction | None:
    try:
        return Direction(direction.strip().lower())
    except ValueError:
        return None


def _parsePinSpec(spec : Any) -> tuple[dict[str, Any] | None, str | None]:
    if not isinstance(spec, dict):
        return None, toolError("Each pin must be an object")
    name = spec.get("name")
    if not name or not isinstance(name, str):
        return None, toolError("Pin name is required")
    direction = _directionFromTool(spec.get("direction", ""))
    if direction is None:
        return None, toolError(f"Invalid pin direction: {spec.get('direction')!r}")
    edge = _edgeFromTool(spec.get("edge", ""))
    if edge is None:
        return None, toolError(f"Invalid pin edge: {spec.get('edge')!r}")
    offset = spec.get("offset")
    if not isinstance(offset, (int, float)):
        return None, toolError("Pin offset is required")
    return {
        "name"      : name,
        "direction" : direction,
        "edge"      : edge,
        "offset"    : float(offset),
    }, None


def _resolveBlock(
    registry : RefRegistry,
    item_ref : str,
) -> tuple[BlockItem | None, str | None]:
    item = registry.resolve(item_ref, kind="item")
    if item is None:
        return None, toolError("Invalid item reference")
    from ...widgets.graphics.items.block import BlockItem
    if not isinstance(item, BlockItem):
        return None, toolError("Item is not a block")
    return item, None


@checked
def _placeBlockPin(
    scene : DiagramScene,
    block : BlockItem,
    spec  : dict[str, Any],
) -> tuple[Any | None, str | None]:
    from ...widgets.graphics.items.block_pin import BlockPinItem
    pin = BlockPinItem()
    pin.setName(spec["name"])
    pin.setDirection(spec["direction"])
    pin.setLocEdge(spec["edge"])
    pin.setLocOffset(spec["offset"])
    scene.addBlockPin(block, pin, undoable=True)
    return pin, None
