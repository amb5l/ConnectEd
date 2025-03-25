from typing import Optional

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .core    import Counter, Settings, DatabaseManager
    from .widgets import MainWindow

count            : Optional['Counter']         = None
settings         : Optional['Settings']        = None
database_manager : Optional['DatabaseManager'] = None
main_window      : Optional['MainWindow']      = None
