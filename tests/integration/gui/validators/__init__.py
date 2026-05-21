"""GUI integration validators (fat); names negotiable."""

from .about        import validateHelpAbout
from .drawing      import validateDrawing, validateDrawingRectangle
from .main_window  import validateMainWindow
from .main_widgets import validateMainWidgets
from .menus        import validateMenus

__all__ = [
    "validateDrawing",
    "validateDrawingRectangle",
    "validateHelpAbout",
    "validateMainWindow",
    "validateMainWidgets",
    "validateMenus"
]
