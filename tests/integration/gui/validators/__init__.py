"""GUI integration validators (fat); names negotiable."""

from .about        import validateHelpAbout
from .diagram      import validateDiagram
from .main_window  import validateMainWindow
from .main_widgets import validateMainWidgets
from .menus        import validateMenus

__all__ = [
    "validateDiagram",
    "validateHelpAbout",
    "validateMainWindow",
    "validateMainWidgets",
    "validateMenus"
]
