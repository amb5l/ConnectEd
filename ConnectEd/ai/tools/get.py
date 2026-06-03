# getters

from typing import Any

from ...core.check import checked

from ..refs  import RefRegistry

from .params import _VIEW_PARAM
from .utils  import aitool, toolOk, toolError

from .private import _drawingSceneFromViewRef

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...widgets.graphics.properties import PropertiesMixin
    from ...widgets.window import Window


@aitool(
    description = "Return ref and name of active view.",
    parameters  = {
        "type"       : "object",
        "properties" : {
            "view" : {"type": "string", "description": "The view reference to get."},
        },
    },
    write = False,
)
@checked
def get_active_view(
    window    : "Window",
    registry  : RefRegistry,
    arguments : dict[str, Any]
) -> str:
    mdi_area = window.mdiArea()
    if mdi_area is None:
        return toolError("No MDI area")
    active_subwindow = mdi_area.activeSubWindow()
    if active_subwindow is None:
        return toolError("No active subwindow")
    view = active_subwindow.widget()
    if view is None:
        return toolError("No view in subwindow")
    from ...widgets.graphics.views.drawing import DrawingView
    if not isinstance(view, DrawingView):
        return toolError("Not a drawing view")
    scene = view.scene()
    if scene is None:
        return toolError("No scene in view")
    from ...widgets.graphics.scenes.drawing import DrawingScene
    if not isinstance(scene, DrawingScene):
        return toolError("Not a drawing scene")
    return toolOk(
        ref  = registry.issue("view", view),
        kind = view.__class__.__name__.replace("View", ""),
        name = scene.name()
    )


@aitool(
    description = "Return diagram sheet name, left edge X, top edge Y, width, height, margin, and border width for a view ref.",
    parameters  = _VIEW_PARAM,
)
@checked
def get_sheet(
    window    : "Window",
    registry  : RefRegistry,
    arguments : dict[str, Any],
) -> str:
    scene, err = _drawingSceneFromViewRef(registry, arguments["view"])
    if scene is None:
        return toolError(err or "Invalid view")
    return toolOk(
        name   = scene.getSheetName(),
        left   = 0.0,
        top    = 0.0,
        width  = scene.getSheetWidth(),
        height = scene.getSheetHeight(),
        margin = scene.getMargin(),
        border = scene.getBorder()
    )


_GET_ITEMS_PARAM = {
    "type"       : "object",
    "properties" : {
        **_VIEW_PARAM["properties"],
        "kinds" : {
            "type"        : "array",
            "description" : (
                "Optional filter: include only items whose kind matches one of "
                "these names (same values as the kind field in the response, "
                "e.g. Block, Port, Gate)."
            ),
            "items"       : {"type": "string"},
        },
        "properties" : {
            "type"        : "array",
            "description" : (
                "Optional item property names to include (e.g. X, Y, Width, Name). "
                "When omitted or empty, each item is returned as ref only. "
                "Names with no value on an item are omitted."
            ),
            "items"       : {"type": "string"},
        },
    },
    "required"   : ["view"],
}


@aitool(
    description = (
        "Return top-level diagram items in a view. By default each item is a ref "
        "only; pass properties to include named item property values. "
        "Optionally filter by item kind."
    ),
    parameters  = _GET_ITEMS_PARAM,
)
@checked
def get_items(
    window    : "Window",
    registry  : RefRegistry,
    arguments : dict[str, Any],
) -> str:
    scene, err = _drawingSceneFromViewRef(registry, arguments["view"])
    if scene is None:
        return toolError(err or "Invalid view")

    kinds_filter, err = _parseStringListArg(arguments.get("kinds"), "kinds")
    if err is not None:
        return err
    kinds_filter = frozenset(kinds_filter) if kinds_filter else None

    properties_filter, err = _parseStringListArg(
        arguments.get("properties"),
        "properties",
    )
    if err is not None:
        return err

    from ...widgets.graphics.items        import ItemMixin
    from ...widgets.graphics.items.node    import NodeItem
    from ...widgets.graphics.items.segment import SegmentItem
    from ...widgets.graphics.properties    import PropertiesMixin
    items_out : list[dict[str, Any]] = []
    for item in scene.items():
        if isinstance(item, NodeItem | SegmentItem):
            continue
        if item.parentItem() is not None:
            continue
        if not isinstance(item, ItemMixin):
            continue
        kind = item.settingsName()
        if kinds_filter is not None and kind not in kinds_filter:
            continue
        row : dict[str, Any] = {
            "ref" : registry.issue("item", item),
        }
        if properties_filter and isinstance(item, PropertiesMixin):
            prop_values = _itemPropertyValues(item, properties_filter)
            if prop_values:
                row["properties"] = prop_values
        items_out.append(row)
    items_out.sort(key=lambda row : row["ref"])
    return toolOk(items=items_out)


def _parseStringListArg(
    value_in   : Any,
    param_name : str,
) -> tuple[list[str] | None, str | None]:
    if value_in is None:
        return None, None
    if not isinstance(value_in, list):
        return None, toolError(f"{param_name} must be an array")
    values : list[str] = []
    for index, value in enumerate(value_in):
        if not isinstance(value, str) or not value.strip():
            return None, toolError(
                f"{param_name}[{index}] must be a non-empty string",
            )
        values.append(value.strip())
    if not values:
        return None, None
    return values, None


def _itemPropertyValues(
    item               : "PropertiesMixin",
    properties_filter  : list[str],
) -> dict[str, Any]:
    values : dict[str, Any] = {}
    for name in properties_filter:
        if not item.properties.has(name):
            continue
        values[name] = _jsonPropertyValue(item.properties.value(name))
    return values


def _jsonPropertyValue(value : Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    from ...core.utils import val2str
    return val2str(value)
