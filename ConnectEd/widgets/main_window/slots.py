import functools
from typing import Callable, Type, TypeVar, cast

from PyQt6.QtWidgets import QMessageBox

from ...core    import logger
from ...widgets import DrawingView, DiagramView

from ... import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...widgets import MainWindow

T = TypeVar('T')

def withCurrentWidget(widget_type: Type[T]) -> Callable[[Callable[['Slots', T], None]], Callable[['Slots'], None]]:
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
                raise ValueError(f'{current_widget} is not a {widget_type} or subclass')
        return wrapper
    return decorator

def withCurrentWidgetCheckable(widget_type: Type[T], action_name: str) -> Callable[[Callable[['Slots', T, bool], None]], Callable[['Slots'], None]]:
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
            else:
                raise ValueError(f'{current_widget} is not a {widget_type} or subclass')
        return wrapper
    return decorator

class Slots:
    _parent : 'MainWindow'

    def __init__(self : 'Slots', parent : 'MainWindow') -> None:
        self._parent = parent

    def fileNewDesign(self : 'Slots') -> None:
        hub.db_model.newItem(hub.db_model.designs)

    def fileNewLibrary(self : 'Slots') -> None:
        hub.db_model.newItem(hub.db_model.libraries)

    def fileOpen(self : 'Slots') -> None:
        hub.db_model.open()

    @withCurrentWidget(DrawingView)
    def fileSave(self : 'Slots', widget: DrawingView) -> None:
        hub.db_model.saveScene(widget.scene())

    @withCurrentWidget(DrawingView)
    def fileSaveAs(self : 'Slots', widget: DrawingView) -> None:
        hub.db_model.saveAsScene(widget.scene())

    def fileExit(self : 'Slots') -> None:
        self._parent.close()

    @withCurrentWidget(DrawingView)
    def editCancel(self : 'Slots', widget: DrawingView) -> None:
        widget.editCancel()

    @withCurrentWidget(DrawingView)
    def editComplete(self : 'Slots', widget: DrawingView) -> None:
        widget.editComplete()

    @withCurrentWidget(DrawingView)
    def editSlide(self : 'Slots', widget: DrawingView) -> None:
        widget.editSlide()

    @withCurrentWidget(DrawingView)
    def editMove(self : 'Slots', widget: DrawingView) -> None:
        widget.editMove()

    @withCurrentWidget(DrawingView)
    def viewZoomAll(self : 'Slots', widget: DrawingView) -> None:
        widget.viewZoomAll()

    @withCurrentWidget(DiagramView)
    def viewZoomSheet(self : 'Slots', widget: DiagramView) -> None:
        widget.viewZoomSheet()

    @withCurrentWidget(DrawingView)
    def viewZoomWindow(self : 'Slots', widget: DrawingView) -> None:
        widget.viewZoomWindow()

    @withCurrentWidget(DrawingView)
    def viewZoomIn(self : 'Slots', widget: DrawingView) -> None:
        widget.viewZoomIn()

    @withCurrentWidget(DrawingView)
    def viewZoomOut(self : 'Slots', widget: DrawingView) -> None:
        widget.viewZoomOut()

    @withCurrentWidget(DrawingView)
    def viewPan(self : 'Slots', widget: DrawingView) -> None:
        widget.viewPan()

    @withCurrentWidget(DrawingView)
    def viewPanUp(self : 'Slots', widget: DrawingView) -> None:
        widget.viewPanUp()

    @withCurrentWidget(DrawingView)
    def viewPanDown(self : 'Slots', widget: DrawingView) -> None:
        widget.viewPanDown()

    @withCurrentWidget(DrawingView)
    def viewPanLeft(self : 'Slots', widget: DrawingView) -> None:
        widget.viewPanLeft()

    @withCurrentWidget(DrawingView)
    def viewPanRight(self : 'Slots', widget: DrawingView) -> None:
        widget.viewPanRight()

    @withCurrentWidgetCheckable(DrawingView, 'viewGridDisplay')
    def viewGridDisplay(self : 'Slots', widget: DrawingView, checked: bool) -> None:
        widget.viewGridDisplay(checked)

    @withCurrentWidgetCheckable(DrawingView, 'viewGridSnap')
    def viewGridSnap(self : 'Slots', widget: DrawingView, checked: bool) -> None:
        widget.viewGridSnap(checked)

    @withCurrentWidget(DrawingView)
    def placeRectangle(self : 'Slots', widget: DrawingView) -> None:
        widget.placeRectangle()

    def windowExplorer(self : 'Slots') -> None:
        self._parent.explorer.show()
        self._parent.explorer.raise_()

    def windowMessages(self : 'Slots') -> None:
        self._parent.messages_viewer.show()
        self._parent.messages_viewer.raise_()

    def windowTranscript(self : 'Slots') -> None:
        self._parent.transcript_viewer.show()
        self._parent.transcript_viewer.raise_()

    def windowLog(self : 'Slots') -> None:
        self._parent.log_viewer.show()
        self._parent.log_viewer.raise_()

    def windowNext(self : 'Slots') -> None:
        self._parent.mdi_area.nextSubWindow()

    def windowPrevious(self : 'Slots') -> None:
        self._parent.mdi_area.previousSubWindow()

    def helpAbout(self : 'Slots') -> None:
        logger.debug('helpAbout')
        QMessageBox.about(self._parent, 'About', 'ConnectEd')
