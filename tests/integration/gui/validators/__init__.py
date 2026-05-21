"""GUI integration validators (fat); names negotiable."""

from .about        import validateHelpAbout
from .drawing      import validateDrawingRectangle
from .main_window  import validateMainWindow
from .main_widgets import validateMainWidgets
from .menus        import validateMenus

__all__ = [
    "validateDrawingRectangle",
    "validateHelpAbout",
    "validateMainWindow",
    "validateMainWidgets",
    "validateMenus"
]
