from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QMdiSubWindow

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene

class PropertiesSubWindow(QMdiSubWindow):
    _scene : "DrawingScene"

    def __init__(self : Self, scene: "DrawingScene") -> None:
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self._scene = scene

    def scene(self : Self) -> "DrawingScene":
        return self._scene
