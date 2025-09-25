import functools

from typing import Self, Callable, Type, TypeVar, cast

from PyQt6.QtWidgets import QMessageBox

from ...app import settings, model, window

from ...core.defs import APP_NAME

from ...widgets.graphics.views.drawing import DrawingView
from ...widgets.graphics.views.diagram import DiagramView

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...widgets.window.explorer import Explorer


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
            current_sub_window = window().mdi_area.currentSubWindow()
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
            current_sub_window = window().mdi_area.currentSubWindow()
            if current_sub_window is None:
                return
            current_widget = current_sub_window.widget()
            if isinstance(current_widget, widget_type):
                checked = getattr(window().actions, action_name).isChecked()
                # Cast to T since we know it"s a subclass
                func(self, cast(T, current_widget), checked)
            else:
                raise ValueError(f"{current_widget} is not a {widget_type} or subclass")
        return wrapper
    return decorator

class Slots:
    def __init__(self : Self) -> None:
        pass

    def fileNewDesign(self : Self) -> None:
        window().explorer.newDesign()

    def fileNewLibrary(self : Self) -> None:
        window().explorer.newLibrary()

    def fileOpen(self : Self) -> None:
        window().explorer.openDb()

    @withCurrentWidget(DrawingView)
    def fileSave(self : Self, view: DrawingView) -> None:
        item = model().getDbItemFromScene(view.scene())
        if item:
            item.save()

    @withCurrentWidget(DrawingView)
    def fileSaveAs(self : Self, view: DrawingView) -> None:
        model().saveAsScene(view.scene())

    def fileExit(self : Self) -> None:
        window().close()

    @withCurrentWidget(DrawingView)
    def editUndo(self : Self, view: DrawingView) -> None:
        view.editUndo()

    @withCurrentWidget(DrawingView)
    def editRedo(self : Self, view: DrawingView) -> None:
        view.editRedo()

    @withCurrentWidget(DrawingView)
    def editCut(self : Self, view: DrawingView) -> None:
        view.editCut()

    @withCurrentWidget(DrawingView)
    def editCopy(self : Self, view: DrawingView) -> None:
        view.editCopy()

    @withCurrentWidget(DrawingView)
    def editPaste(self : Self, view: DrawingView) -> None:
        view.editPaste()

    @withCurrentWidget(DrawingView)
    def editDelete(self : Self, view: DrawingView) -> None:
        view.editDelete()

    @withCurrentWidget(DrawingView)
    def editDuplicate(self : Self, view: DrawingView) -> None:
        view.editDuplicate()

    @withCurrentWidget(DrawingView)
    def editSelectArea(self : Self, view: DrawingView) -> None:
        view.editSelectArea()

    @withCurrentWidget(DrawingView)
    def editSelectAll(self : Self, view: DrawingView) -> None:
        view.editSelectAll()

    @withCurrentWidget(DrawingView)
    def editProperties(self : Self, view: DrawingView) -> None:
        view.editProperties()

    @withCurrentWidget(DrawingView)
    def editAppearance(self : Self, view: DrawingView) -> None:
        view.editAppearance()

    @withCurrentWidget(DrawingView)
    def editQuery(self : Self, view: DrawingView) -> None:
        view.editQuery()

    @withCurrentWidget(DrawingView)
    def viewZoomAll(self : Self, view: DrawingView) -> None:
        view.viewZoomAll()

    @withCurrentWidget(DiagramView)
    def viewZoomSheet(self : Self, view: DiagramView) -> None:
        view.viewZoomSheet()

    @withCurrentWidget(DrawingView)
    def viewZoomArea(self : Self, view: DrawingView) -> None:
        view.viewZoomArea()

    @withCurrentWidget(DrawingView)
    def viewZoomIn(self : Self, view: DrawingView) -> None:
        view.viewZoomIn()

    @withCurrentWidget(DrawingView)
    def viewZoomOut(self : Self, view: DrawingView) -> None:
        view.viewZoomOut()

    @withCurrentWidget(DrawingView)
    def viewPan(self : Self, view: DrawingView) -> None:
        view.viewPan()

    @withCurrentWidget(DrawingView)
    def viewPanUp(self : Self, view: DrawingView) -> None:
        view.viewPanUp()

    @withCurrentWidget(DrawingView)
    def viewPanDown(self : Self, view: DrawingView) -> None:
        view.viewPanDown()

    @withCurrentWidget(DrawingView)
    def viewPanLeft(self : Self, view: DrawingView) -> None:
        view.viewPanLeft()

    @withCurrentWidget(DrawingView)
    def viewPanRight(self : Self, view: DrawingView) -> None:
        view.viewPanRight()

    @withCurrentWidgetCheckable(DrawingView, "viewGridDisplay")
    def viewGridDisplay(self : Self, view: DrawingView, checked: bool) -> None:
        view.viewGridDisplay(checked)

    @withCurrentWidgetCheckable(DrawingView, "viewGridSnap")
    def viewGridSnap(self : Self, view: DrawingView, checked: bool) -> None:
        view.viewGridSnap(checked)

    @withCurrentWidget(DrawingView)
    def viewThemeDark(self : Self, view: DrawingView) -> None:
        settings().set("display/theme", "dark")
        view.scene().update()

    @withCurrentWidget(DrawingView)
    def viewThemeLightMono(self : Self, view: DrawingView) -> None:
        settings().set("display/theme", "light_mono")
        view.scene().update()

    @withCurrentWidget(DrawingView)
    def placePort(self : Self, view: DrawingView) -> None:
        view.placePort()

    @withCurrentWidget(DrawingView)
    def placeBlock(self : Self, view: DrawingView) -> None:
        view.placeBlock()

    @withCurrentWidget(DrawingView)
    def placeBlockPin(self : Self, view: DrawingView) -> None:
        view.placeBlockPin()

    @withCurrentWidget(DrawingView)
    def placeRectangle(self : Self, view: DrawingView) -> None:
        view.placeRectangle()

    @withCurrentWidget(DrawingView)
    def placeTextBlock(self : Self, view: DrawingView) -> None:
        view.placeTextBlock()

    @withCurrentWidget(DrawingView)
    def placeText(self : Self, view: DrawingView) -> None:
        view.placeText()

    def windowExplorer(self : Self) -> None:
        window().explorer_dock.show()
        window().explorer_dock.raise_()

    def windowMessages(self : Self) -> None:
        window().messages_viewer.show()
        window().messages_viewer.raise_()

    def windowTranscript(self : Self) -> None:
        window().transcript_viewer.show()
        window().transcript_viewer.raise_()

    def windowLog(self : Self) -> None:
        window().log_viewer.show()
        window().log_viewer.raise_()

    def windowNext(self : Self) -> None:
        window().mdi_area.nextSubWindow()

    def windowPrevious(self : Self) -> None:
        window().mdi_area.previousSubWindow()

    def helpAbout(self : Self) -> None:
        QMessageBox.about(window(), "About", APP_NAME)
