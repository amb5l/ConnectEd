from typing import Self, Optional

from PyQt6.QtWidgets import QApplication

from .core.nv        import Settings
from .core.db        import Model
from .widgets.window import Window


class ConnectEdApp(QApplication):
    # instance attributes
    settings : Optional[Settings]
    model    : Optional[Model]
    window   : Optional[Window]

    def __init__(self : Self, argv : list[str]) -> None:
        super().__init__(argv)
        self.settings = None
        self.model    = None
        self.window   = None
