import os

from typing import Optional

from PyQt6.QtWidgets import QApplication

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .core    import NameCounter, Settings, Model
    from .widgets import MainWindow

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

name_counter : Optional["NameCounter"]  = None
settings     : Optional["Settings"]     = None
model        : Optional["Model"]        = None
main_window  : Optional["MainWindow"]   = None
app          : Optional["QApplication"] = None
