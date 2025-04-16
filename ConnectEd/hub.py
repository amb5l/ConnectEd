from typing import Optional

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .core    import NameCounter, Settings, Model
    from .widgets import MainWindow

name_counter : Optional['NameCounter'] = None
settings     : Optional['Settings']    = None
model        : Optional['Model']       = None
main_window  : Optional['MainWindow']  = None
