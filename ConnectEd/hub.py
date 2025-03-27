from typing import Optional

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .core    import NameCounter, Settings, DbModel
    from .widgets import MainWindow

name_counter : Optional['NameCounter']     = None
settings     : Optional['Settings']        = None
db_model     : Optional['DbModel'] = None
main_window  : Optional['MainWindow']      = None
