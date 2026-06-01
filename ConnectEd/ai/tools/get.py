# getters

from typing import Any

from ...core.check import checked

from ..refs  import RefRegistry

from .params import _VIEW_PARAM
from .utils  import aitool, toolOk, toolError

from .private import _drawingSceneFromViewRef

from typing import TYPE_CHECKING
if TYPE_CHECKING:
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


@aitool(
    description = (
        "Return refs, scene positions, and axis-aligned bounding rects for "
        "top-level diagram items in a view (for layout and finding free space)."
    ),
    parameters  = _VIEW_PARAM,
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
    from ...widgets.graphics.items        import ItemMixin
    from ...widgets.graphics.items.node    import NodeItem
    from ...widgets.graphics.items.segment import SegmentItem
    items_out : list[dict[str, Any]] = []
    for item in scene.items():
        if isinstance(item, NodeItem | SegmentItem):
            continue
        if item.parentItem() is not None:
            continue
        if not isinstance(item, ItemMixin):
            continue
        pos    = item.scenePos()
        bounds = item.mapToScene(item.boundingRect()).boundingRect()
        items_out.append({
            "ref"    : registry.issue("item", item),
            "kind"   : item.settingsName(),
            "x"      : pos.x(),
            "y"      : pos.y(),
            "left"   : bounds.left(),
            "top"    : bounds.top(),
            "width"  : bounds.width(),
            "height" : bounds.height(),
        })
    items_out.sort(key=lambda row : (row["top"], row["left"], row["ref"]))
    return toolOk(items=items_out)
