from typing import Any

from PyQt6.QtCore import QPointF

from ...core.check import checked

from ..refs   import RefRegistry
from .utils   import aitool, toolError, toolOk
from .private import _drawingSceneFromViewRef

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...widgets.window import Window


_BLOCK_PARAM_PROPS = {
    "view"   : {
        "type"        : "string",
        "description" : "Diagram view reference from get_active_view.",
    },
    "label"  : {
        "type"        : "string",
        "description" : "Instance label (e.g. U1, U2, U3).",
    },
    "name"   : {
        "type"        : "string",
        "description" : "HDL module/entity name.",
    },
    "left"   : {
        "type"        : "number",
        "description" : "Top-left X in scene coordinates.",
    },
    "top"    : {
        "type"        : "number",
        "description" : "Top-left Y in scene coordinates.",
    },
    "width"  : {
        "type"        : "number",
        "description" : "Block width.",
    },
    "height" : {
        "type"        : "number",
        "description" : "Block height.",
    }
}

@aitool(
    description = (
        "Add a block to the diagram with an HDL instance label, HDL module "
        "name, top-left position, and size. Returns the block's reference."
    ),
    parameters  = {
        "type"       : "object",
        "properties" : _BLOCK_PARAM_PROPS,
        "required"   : list(_BLOCK_PARAM_PROPS.keys()),
    },
    write = True,
)
@checked
def add_block(
    window    : "Window",
    registry  : RefRegistry,
    arguments : dict[str, Any],
) -> str:
    if arguments["width"] <= 0.0 or arguments["height"] <= 0.0:
        return toolError("width and height must be positive")
    scene, err = _drawingSceneFromViewRef(registry, arguments["view"])
    if scene is None:
        return toolError(err or "Invalid view")
    from ...widgets.graphics.items.block import BlockItem
    p1 = QPointF(arguments["left"], arguments["top"])
    p2 = p1 + QPointF(arguments["width"], arguments["height"])
    block = BlockItem(p1, p2)
    block.setLabel(arguments["label"])
    block.setName(arguments["name"])
    scene.addItems([block], undoable=True)
    return toolOk(ref = registry.issue("item", block))
