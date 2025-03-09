from PyQt6.QtWidgets import QMessageBox

from ....core    import logger
from ....widgets import Drawing, Diagram

import functools
from typing import Callable, Type, TypeVar, cast

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

def with_current_widget_checkable(widget_type: Type[T], action_name: str) -> Callable[[Callable[['Slots', T, bool], None]], Callable[['Slots'], None]]:
    """
    Decorator for checkable actions that gets the current widget from the MDI area,
    checks if it's of the specified type, and passes the checked state from the action.

    Args:
        widget_type: The type to check the current widget against
        action_name: The name of the action to get the checked state from

    Returns:
        A decorator function
    """
    def decorator(func: Callable[['Slots', T, bool], None]) -> Callable[['Slots'], None]:
        @functools.wraps(func)
        def wrapper(self: 'Slots') -> None:
            current_sub_window = self._parent.mdi_area.currentSubWindow()
            if current_sub_window is None:
                return
            current_widget = current_sub_window.widget()
            if isinstance(current_widget, widget_type):
                checked = getattr(self._parent.commands.actions, action_name).isChecked()
                func(self, cast(T, current_widget), checked)
        return wrapper
    return decorator

class Slots:
    _parent : 'MainWindow'

    def __init__(self : 'Slots', parent : 'MainWindow') -> None:
        self._parent = parent

    def fileExit(self : 'Slots') -> None:
        self._parent.close()

    @with_current_widget(Drawing)
    def editCancel(self : 'Slots', widget: Drawing) -> None:
        widget.editCancel()

    @with_current_widget(Drawing)
    def viewZoomAll(self : 'Slots', widget: Drawing) -> None:
        widget.viewZoomAll()

    @with_current_widget(Diagram)
    def viewZoomSheet(self : 'Slots', widget: Diagram) -> None:
        widget.viewZoomSheet()

    @with_current_widget(Drawing)
    def viewZoomWindow(self : 'Slots', widget: Drawing) -> None:
        widget.viewZoomWindow()

    @with_current_widget(Drawing)
    def viewZoomIn(self : 'Slots', widget: Drawing) -> None:
        widget.viewZoomIn()

    @with_current_widget(Drawing)
    def viewZoomOut(self : 'Slots', widget: Drawing) -> None:
        widget.viewZoomOut()

    @with_current_widget(Drawing)
    def viewPanUp(self : 'Slots', widget: Drawing) -> None:
        widget.viewPanUp()

    @with_current_widget(Drawing)
    def viewPanDown(self : 'Slots', widget: Drawing) -> None:
        widget.viewPanDown()

    @with_current_widget(Drawing)
    def viewPanLeft(self : 'Slots', widget: Drawing) -> None:
        widget.viewPanLeft()

    @with_current_widget(Drawing)
    def viewPanRight(self : 'Slots', widget: Drawing) -> None:
        widget.viewPanRight()

    @with_current_widget_checkable(Drawing, 'viewGridDisplay')
    def viewGridDisplay(self : 'Slots', widget: Drawing, checked: bool) -> None:
        widget.viewGridDisplay(checked)

    @with_current_widget_checkable(Drawing, 'viewGridSnap')
    def viewGridSnap(self : 'Slots', widget: Drawing, checked: bool) -> None:
        widget.viewGridSnap(checked)

    @with_current_widget(Drawing)
    def placeRectangle(self : 'Slots', widget: Drawing) -> None:
        widget.placeRectangle()

    def windowMessages(self : 'Slots') -> None:
        self._parent.msg_viewer.show()
        self._parent.msg_viewer.raise_()

    def windowLog(self : 'Slots') -> None:
        self._parent.log_viewer.show()
        self._parent.log_viewer.raise_()

    def helpAbout(self : 'Slots') -> None:
        logger.debug('helpAbout')
        QMessageBox.about(self._parent, 'About', 'ConnectEd')
