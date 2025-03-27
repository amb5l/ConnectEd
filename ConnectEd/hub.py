from typing import Optional

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .core    import NameCounter, Settings, DatabaseManager
    from .widgets import MainWindow

name_counter     : Optional['NameCounter']     = None
settings         : Optional['Settings']        = None
database_manager : Optional['DatabaseManager'] = None
main_window      : Optional['MainWindow']      = None
