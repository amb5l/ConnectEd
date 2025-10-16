from typing import Self

from PyQt6.QtWidgets import QMdiSubWindow

from ...core.log import logger

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...widgets.graphics.scenes.drawing import DrawingScene


class SubWindow(QMdiSubWindow):
    def scene(self : Self) -> "DrawingScene | None":
        from ...widgets.graphics.views.drawing import DrawingView
        from ...widgets.graphics.scenes.drawing import DrawingScene
        widget = self.widget()
        if isinstance(widget, DrawingView):
            scene = widget.scene()
            if isinstance(scene, DrawingScene):
                return scene
            else:
                logger().warning(f"Expected DrawingScene: {type(scene)}")
                return None
        else:
            logger().warning(f"Expected DrawingView, got: {type(widget)}")
            return None
