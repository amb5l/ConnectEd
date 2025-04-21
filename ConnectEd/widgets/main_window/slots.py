import functools

from typing import Self, Callable, Type, TypeVar, cast

from PyQt6.QtWidgets import QMessageBox

from ...core    import logger
from ...widgets import DrawingView, DiagramView

from ... import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...widgets import MainWindow

T = TypeVar("T")

def withCurrentWidget(widget_type: Type[T]) -> Callable[[Callable[["Slots", T], None]], Callable[["Slots"], None]]:
    """
    Decorator that gets the current widget from the MDI area and checks if it"s of the specified type
    or a subclass of it before calling the decorated method.

    Args:
        widget_type: The type to check the current widget against

    Returns:
        A decorator function
    """
    def decorator(func: Callable[["Slots", T], None]) -> Callable[["Slots"], None]:
        @functools.wraps(func)
        def wrapper(self : "Slots") -> None:
            current_sub_window = self._parent.mdi_area.currentSubWindow()
            if current_sub_window is None:
                return
            current_widget = current_sub_window.widget()
            if isinstance(current_widget, widget_type):
                # Cast to T since we know it"s a subclass
                func(self, cast(T, current_widget))
            else:
                raise ValueError(f"{current_widget} is not a {widget_type} or subclass")
        return wrapper
    return decorator

def withCurrentWidgetCheckable(widget_type: Type[T], action_name: str) -> Callable[[Callable[["Slots", T, bool], None]], Callable[["Slots"], None]]:
    """
    Decorator for checkable actions that gets the current widget from the MDI area,
    checks if it"s of the specified type or a subclass, and passes the checked state from the action.

    Args:
        widget_type: The type to check the current widget against
        action_name: The name of the action to get the checked state from

    Returns:
        A decorator function
    """
    def decorator(func: Callable[["Slots", T, bool], None]) -> Callable[["Slots"], None]:
        @functools.wraps(func)
        def wrapper(self : "Slots") -> None:
            current_sub_window = self._parent.mdi_area.currentSubWindow()
            if current_sub_window is None:
                return
            current_widget = current_sub_window.widget()
            if isinstance(current_widget, widget_type):
                checked = getattr(self._parent.actions, action_name).isChecked()
                # Cast to T since we know it"s a subclass
                func(self, cast(T, current_widget), checked)
            else:
                raise ValueError(f"{current_widget} is not a {widget_type} or subclass")
        return wrapper
    return decorator

class Slots:
    _parent : "MainWindow"

    def __init__(self : Self, parent : "MainWindow") -> None:
        self._parent = parent

    def fileNewDesign(self : Self) -> None:
        hub.main_window.explorer.widget().newDesign()

    def fileNewLibrary(self : Self) -> None:
        hub.main_window.explorer.widget().newLibrary()

    def fileOpen(self : Self) -> None:
        hub.main_window.explorer.widget().openItem()

    @withCurrentWidget(DrawingView)
    def fileSave(self : Self, widget: DrawingView) -> None:
        item = hub.model.getDbItemFromScene(widget.scene())
        if item:
            item.save()

    @withCurrentWidget(DrawingView)
    def fileSaveAs(self : Self, widget: DrawingView) -> None:
        hub.model.saveAsScene(widget.scene())

    def fileExit(self : Self) -> None:
        self._parent.close()

    @withCurrentWidget(DrawingView)
    def editUndo(self : Self, widget: DrawingView) -> None:
        widget.editUndo()

    @withCurrentWidget(DrawingView)
    def editRedo(self : Self, widget: DrawingView) -> None:
        widget.editRedo()

    @withCurrentWidget(DrawingView)
    def editCancel(self : Self, widget: DrawingView) -> None:
        widget.editCancel()

    @withCurrentWidget(DrawingView)
    def editComplete(self : Self, widget: DrawingView) -> None:
        widget.editComplete()

    @withCurrentWidget(DrawingView)
    def editCut(self : Self, widget: DrawingView) -> None:
        widget.editCut()

    @withCurrentWidget(DrawingView)
    def editCopy(self : Self, widget: DrawingView) -> None:
        widget.editCopy()

    @withCurrentWidget(DrawingView)
    def editPaste(self : Self, widget: DrawingView) -> None:
        widget.editPaste()

    @withCurrentWidget(DrawingView)
    def editDelete(self : Self, widget: DrawingView) -> None:
        widget.editDelete()

    @withCurrentWidget(DrawingView)
    def editSlide(self : Self, widget: DrawingView) -> None:
        widget.editSlide()

    @withCurrentWidget(DrawingView)
    def editMove(self : Self, widget: DrawingView) -> None:
        widget.editMove()

    @withCurrentWidget(DrawingView)
    def viewZoomAll(self : Self, widget: DrawingView) -> None:
        widget.viewZoomAll()

    @withCurrentWidget(DiagramView)
    def viewZoomSheet(self : Self, widget: DiagramView) -> None:
        widget.viewZoomSheet()

    @withCurrentWidget(DrawingView)
    def viewZoomWindow(self : Self, widget: DrawingView) -> None:
        widget.viewZoomWindow()

    @withCurrentWidget(DrawingView)
    def viewZoomIn(self : Self, widget: DrawingView) -> None:
        widget.viewZoomIn()

    @withCurrentWidget(DrawingView)
    def viewZoomOut(self : Self, widget: DrawingView) -> None:
        widget.viewZoomOut()

    @withCurrentWidget(DrawingView)
    def viewPan(self : Self, widget: DrawingView) -> None:
        widget.viewPan()

    @withCurrentWidget(DrawingView)
    def viewPanUp(self : Self, widget: DrawingView) -> None:
        widget.viewPanUp()

    @withCurrentWidget(DrawingView)
    def viewPanDown(self : Self, widget: DrawingView) -> None:
        widget.viewPanDown()

    @withCurrentWidget(DrawingView)
    def viewPanLeft(self : Self, widget: DrawingView) -> None:
        widget.viewPanLeft()

    @withCurrentWidget(DrawingView)
    def viewPanRight(self : Self, widget: DrawingView) -> None:
        widget.viewPanRight()

    @withCurrentWidgetCheckable(DrawingView, "viewGridDisplay")
    def viewGridDisplay(self : Self, widget: DrawingView, checked: bool) -> None:
        widget.viewGridDisplay(checked)

    @withCurrentWidgetCheckable(DrawingView, "viewGridSnap")
    def viewGridSnap(self : Self, widget: DrawingView, checked: bool) -> None:
        widget.viewGridSnap(checked)

    @withCurrentWidget(DrawingView)
    def placeRectangle(self : Self, widget: DrawingView) -> None:
        widget.placeRectangle()

    def windowExplorer(self : Self) -> None:
        self._parent.explorer.show()
        self._parent.explorer.raise_()

    def windowMessages(self : Self) -> None:
        self._parent.messages_viewer.show()
        self._parent.messages_viewer.raise_()

    def windowTranscript(self : Self) -> None:
        self._parent.transcript_viewer.show()
        self._parent.transcript_viewer.raise_()

    def windowLog(self : Self) -> None:
        self._parent.log_viewer.show()
        self._parent.log_viewer.raise_()

    def windowNext(self : Self) -> None:
        self._parent.mdi_area.nextSubWindow()

    def windowPrevious(self : Self) -> None:
        self._parent.mdi_area.previousSubWindow()

    def helpAbout(self : Self) -> None:
        logger.debug("helpAbout")
        QMessageBox.about(self._parent, "About", "ConnectEd")
