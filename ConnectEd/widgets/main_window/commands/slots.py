from PyQt6.QtWidgets import QMessageBox

from ....core    import logger
from ....widgets import Drawing, Diagram

import functools
from typing import Callable, Type, TypeVar, cast, Any

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....widgets.main_window import MainWindow

T = TypeVar('T')

def with_current_widget(widget_type: Type[T]) -> Callable[[Callable[['Slots', T], None]], Callable[['Slots'], None]]:
    """
    Decorator that gets the current widget from the MDI area and checks if it's of the specified type
    before calling the decorated method.

    Args:
        widget_type: The type to check the current widget against

    Returns:
        A decorator function
    """
    def decorator(func: Callable[['Slots', T], None]) -> Callable[['Slots'], None]:
        @functools.wraps(func)
        def wrapper(self: 'Slots') -> None:
            current_sub_window = self._parent.mdi_area.currentSubWindow()
            if current_sub_window is None:
                return
            current_widget = current_sub_window.widget()
            if isinstance(current_widget, widget_type):
                func(self, cast(T, current_widget))
        return wrapper
    return decorator

class Slots:
    _parent : 'MainWindow'

    def __init__(self : 'Slots', parent : 'MainWindow') -> None:
        self._parent = parent

    def fileExit(self : 'Slots') -> None:
        self._parent.close()

    @with_current_widget(Drawing)
    def viewZoomAll(self : 'Slots', widget: Drawing) -> None:
        widget.viewZoomAll()

    @with_current_widget(Diagram)
    def viewZoomSheet(self : 'Slots', widget: Diagram) -> None:
        widget.viewZoomSheet()

    @with_current_widget(Drawing)
    def viewZoomIn(self : 'Slots', widget: Drawing) -> None:
        widget.viewZoomIn()

    @with_current_widget(Drawing)
    def viewZoomOut(self : 'Slots', widget: Drawing) -> None:
        widget.viewZoomOut()

    def windowMessages(self : 'Slots') -> None:
        self._parent.msg_viewer.show()
        self._parent.msg_viewer.raise_()

    def windowLog(self : 'Slots') -> None:
        self._parent.log_viewer.show()
        self._parent.log_viewer.raise_()

    def helpAbout(self : 'Slots') -> None:
        logger.debug('helpAbout')
        QMessageBox.about(self._parent, 'About', 'ConnectEd')
