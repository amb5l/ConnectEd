from PyQt6.QtWidgets import QMessageBox

from ...core    import logger
from ...widgets import DrawingView, DiagramView

import functools
from typing import Callable, Type, TypeVar, cast

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...widgets.main_window import MainWindow

T = TypeVar('T')

def with_current_widget(widget_type: Type[T]) -> Callable[[Callable[['Slots', T], None]], Callable[['Slots'], None]]:
    """
    Decorator that gets the current widget from the MDI area and checks if it's of the specified type
    or a subclass of it before calling the decorated method.

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
                # Cast to T since we know it's a subclass
                func(self, cast(T, current_widget))
            else:
                print(f'{current_widget} is not a {widget_type} or subclass')
        return wrapper
    return decorator

def with_current_widget_checkable(widget_type: Type[T], action_name: str) -> Callable[[Callable[['Slots', T, bool], None]], Callable[['Slots'], None]]:
    """
    Decorator for checkable actions that gets the current widget from the MDI area,
    checks if it's of the specified type or a subclass, and passes the checked state from the action.

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
                checked = getattr(self._parent.actions, action_name).isChecked()
                # Cast to T since we know it's a subclass
                func(self, cast(T, current_widget), checked)
        return wrapper
    return decorator

class Slots:
    _parent : 'MainWindow'

    def __init__(self : 'Slots', parent : 'MainWindow') -> None:
        self._parent = parent

    def fileExit(self : 'Slots') -> None:
        self._parent.close()

    @with_current_widget(DrawingView)
    def editCancel(self : 'Slots', widget: DrawingView) -> None:
        widget.editCancel()

    @with_current_widget(DrawingView)
    def editComplete(self : 'Slots', widget: DrawingView) -> None:
        widget.editComplete()

    @with_current_widget(DrawingView)
    def editSlide(self : 'Slots', widget: DrawingView) -> None:
        widget.editSlide()

    @with_current_widget(DrawingView)
    def editMove(self : 'Slots', widget: DrawingView) -> None:
        widget.editMove()

    @with_current_widget(DrawingView)
    def viewZoomAll(self : 'Slots', widget: DrawingView) -> None:
        widget.viewZoomAll()

    @with_current_widget(DiagramView)
    def viewZoomSheet(self : 'Slots', widget: DiagramView) -> None:
        widget.viewZoomSheet()

    @with_current_widget(DrawingView)
    def viewZoomWindow(self : 'Slots', widget: DrawingView) -> None:
        widget.viewZoomWindow()

    @with_current_widget(DrawingView)
    def viewZoomIn(self : 'Slots', widget: DrawingView) -> None:
        widget.viewZoomIn()

    @with_current_widget(DrawingView)
    def viewZoomOut(self : 'Slots', widget: DrawingView) -> None:
        widget.viewZoomOut()

    @with_current_widget(DrawingView)
    def viewPan(self : 'Slots', widget: DrawingView) -> None:
        widget.viewPan()

    @with_current_widget(DrawingView)
    def viewPanUp(self : 'Slots', widget: DrawingView) -> None:
        widget.viewPanUp()

    @with_current_widget(DrawingView)
    def viewPanDown(self : 'Slots', widget: DrawingView) -> None:
        widget.viewPanDown()

    @with_current_widget(DrawingView)
    def viewPanLeft(self : 'Slots', widget: DrawingView) -> None:
        widget.viewPanLeft()

    @with_current_widget(DrawingView)
    def viewPanRight(self : 'Slots', widget: DrawingView) -> None:
        widget.viewPanRight()

    @with_current_widget_checkable(DrawingView, 'viewGridDisplay')
    def viewGridDisplay(self : 'Slots', widget: DrawingView, checked: bool) -> None:
        widget.viewGridDisplay(checked)

    @with_current_widget_checkable(DrawingView, 'viewGridSnap')
    def viewGridSnap(self : 'Slots', widget: DrawingView, checked: bool) -> None:
        widget.viewGridSnap(checked)

    @with_current_widget(DrawingView)
    def placeRectangle(self : 'Slots', widget: DrawingView) -> None:
        widget.placeRectangle()

    def windowMessages(self : 'Slots') -> None:
        print('windowMessages')
        self._parent.msg_viewer.show()
        self._parent.msg_viewer.raise_()

    def windowLog(self : 'Slots') -> None:
        print('windowLog')
        self._parent.log_viewer.show()
        self._parent.log_viewer.raise_()

    def helpAbout(self : 'Slots') -> None:
        logger.debug('helpAbout')
        QMessageBox.about(self._parent, 'About', 'ConnectEd')
