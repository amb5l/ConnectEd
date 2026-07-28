from __future__ import annotations

from ..refs import RefRegistry

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...widgets.graphics.scenes.diagram import DiagramScene


def _sceneFromViewRef(
    registry : RefRegistry,
    view     : str,
) -> tuple[DiagramScene | None, str | None]:
    drawing_view = registry.resolve(view, kind="view")
    if drawing_view is None:
        return None, f"Unknown or stale view: {view!r}"
    from ...widgets.graphics.views.diagram import DiagramView
    if not isinstance(drawing_view, DiagramView):
        return None, "Ref is not a diagram view"
    scene = drawing_view.scene()
    if scene is None:
        return None, "No scene in view"
    from ...widgets.graphics.scenes.diagram import DiagramScene
    if not isinstance(scene, DiagramScene):
        return None, "Not a diagram scene"
    return scene, None


def _drawingSceneFromViewRef(
    registry : RefRegistry,
    view     : str,
) -> tuple[DiagramScene | None, str | None]:
    return _sceneFromViewRef(registry, view)
