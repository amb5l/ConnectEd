import os

from typing import Optional

from PyQt6.QtWidgets import QApplication

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .core.utils     import NameCounter
    from .core.nv        import Settings
    from .core.db        import Model
    from .widgets.splash import Splash
    from .widgets.window import Window

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

name_counter : Optional["NameCounter"]  = None
settings     : Optional["Settings"]     = None
model        : Optional["Model"]        = None
splash       : Optional["Splash"]       = None
window       : Optional["Window"]       = None
app          : Optional["QApplication"] = None
