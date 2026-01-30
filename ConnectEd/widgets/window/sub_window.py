from typing import Self

from PyQt6.QtWidgets import QMdiSubWindow

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...widgets.graphics.views.drawing import DrawingView
    from ...widgets.graphics.scenes.drawing import DrawingScene


class SubWindow(QMdiSubWindow):
    def scene(self : Self) -> "DrawingScene | None":
        view : "DrawingView | None" = self.widget()
        return view.scene() if view else None
