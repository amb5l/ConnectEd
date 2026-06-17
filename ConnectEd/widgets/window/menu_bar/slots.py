import functools

from typing          import Self, TypeVar, cast
from collections.abc import Callable

from PyQt6.QtWidgets import QMdiSubWindow, QMessageBox

from ....app import logger, settings, window

from ....core.defs import APP_NAME

from ....widgets.window.navigator import Navigator

from ....widgets.graphics.views.drawing import DrawingView
from ....widgets.graphics.views.diagram import DiagramView
from ....widgets.graphics.views.symbol  import SymbolView

from ..sub_window import DocSubWindow


T = TypeVar("T")


def withFocusWidget(widget_type: type[T]) -> Callable[[Callable[["Slots", T], None]], Callable[["Slots"], None]]:
    """
    Decorator that gets the current widget from the focus widget and checks if it's
    of the specified type or a subclass of it before calling the decorated method.
    """
    def decorator(func: Callable[["Slots", T], None]) -> Callable[["Slots"], None]:
        @functools.wraps(func)
        def wrapper(self : "Slots") -> None:
            current_widget = window().focusWidget()
            if current_widget is None:
                return
            if isinstance(current_widget, widget_type):
                func(self, cast(T, current_widget))
            else:
                raise ValueError(f"{current_widget} is not a {widget_type} or subclass")
        return wrapper
    return decorator


def withMdiSubWindow(
    func : Callable[["Slots", DocSubWindow], None],
) -> Callable[["Slots"], None]:
    """
    Decorator that gets the active subwindow from the MDI area and checks
    that it is a ``SubWindow`` before calling the decorated method.
    """
    @functools.wraps(func)
    def wrapper(self : "Slots") -> None:
        mdi_area = window().mdiArea()
        if mdi_area is None:
            return
        current_subwindow = mdi_area.activeSubWindow()
        if current_subwindow is None:
            return
        func(self, current_subwindow)
    return wrapper


def withMdiWidget(widget_type: type[T]) -> Callable[[Callable[["Slots", T], None]], Callable[["Slots"], None]]:
    """
    Decorator that gets the current widget from the MDI area and checks if it's
    of the specified type or a subclass of it before calling the decorated method.

    Args:
        widget_type: The type to check the current widget against

    Returns:
        A decorator function
    """
    def decorator(func: Callable[["Slots", T], None]) -> Callable[["Slots"], None]:
        @functools.wraps(func)
        def wrapper(self : "Slots") -> None:
            current_subwindow = window().mdiArea().currentSubWindow()
            if current_subwindow is None:
                return
            current_widget = current_subwindow.widget()
            if isinstance(current_widget, widget_type):
                # Cast to T since we know it"s a subclass
                func(self, cast(T, current_widget))
            else:
                raise ValueError(f"{current_widget} is not a {widget_type} or subclass")
        return wrapper
    return decorator


def withMdiWidgetCheckable(
    widget_type : type[T],
    action_name : str
) -> Callable[[Callable[["Slots", T, bool], None]], Callable[["Slots"], None]]:
    """
    Decorator for checkable actions that gets the current widget from the MDI
    area, checks if it's of the specified type or a subclass, and passes the
    checked state from the action.

    Args:
        widget_type: The type to check the current widget against
        action_name: The name of the action to get the checked state from

    Returns:
        A decorator function
    """
    def decorator(func: Callable[["Slots", T, bool], None]) -> Callable[["Slots"], None]:
        @functools.wraps(func)
        def wrapper(self : "Slots") -> None:
            current_subwindow = window().mdiArea().currentSubWindow()
            if current_subwindow is None:
                return
            current_widget = current_subwindow.widget()
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

    def fileNew(self : Self) -> None:
        window().navigator().fileNew()

    def fileOpen(self : Self) -> None:
        window().navigator().fileOpen()

    @withMdiSubWindow
    def fileSave(self : Self, subwindow : QMdiSubWindow) -> None:
        if isinstance(subwindow, DocSubWindow):
            window().navigator().fileSave(subwindow)
        else:
            logger().error("Subwindow is not a DocSubWindow")

    @withMdiSubWindow
    def fileSaveAs(self : Self, subwindow : QMdiSubWindow) -> None:
        if isinstance(subwindow, DocSubWindow):
            window().navigator().fileSaveAs(subwindow)
        else:
            logger().error("Subwindow is not a DocSubWindow")

    @withMdiSubWindow
    def fileClose(self : Self, subwindow : QMdiSubWindow) -> None:
        if isinstance(subwindow, DocSubWindow):
            window().navigator().fileClose(subwindow)
        else:
            # handle other types of subwindows
            pass

    def fileOpenMRU1(self : Self) -> None:
        window().navigator().docLoad(settings().getMRU()[0])

    def fileOpenMRU2(self : Self) -> None:
        window().navigator().docLoad(settings().getMRU()[1])

    def fileOpenMRU3(self : Self) -> None:
        window().navigator().docLoad(settings().getMRU()[2])

    def fileOpenMRU4(self : Self) -> None:
        window().navigator().docLoad(settings().getMRU()[3])

    def fileOpenMRU5(self : Self) -> None:
        window().navigator().docLoad(settings().getMRU()[4])

    def fileOpenMRU6(self : Self) -> None:
        window().navigator().docLoad(settings().getMRU()[5])

    def fileOpenMRU7(self : Self) -> None:
        window().navigator().docLoad(settings().getMRU()[6])

    def fileOpenMRU8(self : Self) -> None:
        window().navigator().docLoad(settings().getMRU()[7])

    def fileOpenMRU9(self : Self) -> None:
        window().navigator().docLoad(settings().getMRU()[8])

    def fileExit(self : Self) -> None:
        window().close()

    @withMdiWidget(DrawingView)
    def editCancel(self : Self, view : DrawingView) -> None:
        view.editCancel()

    @withMdiWidget(DrawingView)
    def editUndo(self : Self, view : DrawingView) -> None:
        view.editUndo()

    @withMdiWidget(DrawingView)
    def editRedo(self : Self, view : DrawingView) -> None:
        view.editRedo()

    @withMdiWidget(DrawingView)
    def editCut(self : Self, view : DrawingView) -> None:
        view.editCut()

    @withFocusWidget(DrawingView | Navigator)
    def editCopy(self : Self, widget : DrawingView) -> None:
        widget.ui.editCopy()

    @withFocusWidget(DrawingView | Navigator)
    def editPaste(self : Self, widget : DrawingView) -> None:
        widget.ui.editPaste()

    @withMdiWidget(DrawingView)
    def editDelete(self : Self, view : DrawingView) -> None:
        view.editDelete()

    @withMdiWidget(DrawingView)
    def editDuplicate(self : Self, view : DrawingView) -> None:
        view.editDuplicate()

    @withMdiWidget(DrawingView)
    def editSelectArea(self : Self, view : DrawingView) -> None:
        view.editSelectArea()

    @withMdiWidget(DrawingView)
    def editSelectAll(self : Self, view : DrawingView) -> None:
        view.editSelectAll()

    @withMdiWidget(DrawingView)
    def editRotateCW(self : Self, view : DrawingView) -> None:
        view.editRotateCW()

    @withMdiWidget(DrawingView)
    def editRotateCCW(self : Self, view : DrawingView) -> None:
        view.editRotateCCW()

    @withMdiWidget(DrawingView)
    def editProperties(self : Self, view : DrawingView) -> None:
        view.editItemProperties()

    @withMdiWidget(DrawingView)
    def editAppearance(self : Self, view : DrawingView) -> None:
        view.editAppearance()

    @withMdiWidget(DrawingView)
    def editQuery(self : Self, view : DrawingView) -> None:
        view.editQuery()

    @withMdiWidget(DrawingView)
    def viewZoomAll(self : Self, view : DrawingView) -> None:
        view.viewZoomAll()

    @withMdiWidget(DiagramView)
    def viewZoomSheet(self : Self, view : DiagramView) -> None:
        view.viewZoomSheet()

    @withMdiWidget(DrawingView)
    def viewZoomArea(self : Self, view : DrawingView) -> None:
        view.viewZoomArea()

    @withMdiWidget(DrawingView)
    def viewZoomIn(self : Self, view : DrawingView) -> None:
        view.viewZoomIn()

    @withMdiWidget(DrawingView)
    def viewZoomOut(self : Self, view : DrawingView) -> None:
        view.viewZoomOut()

    @withMdiWidget(DrawingView)
    def viewPan(self : Self, view : DrawingView) -> None:
        view.viewPan()

    @withMdiWidget(DrawingView)
    def viewPanUp(self : Self, view : DrawingView) -> None:
        view.viewPanUp()

    @withMdiWidget(DrawingView)
    def viewPanDown(self : Self, view : DrawingView) -> None:
        view.viewPanDown()

    @withMdiWidget(DrawingView)
    def viewPanLeft(self : Self, view : DrawingView) -> None:
        view.viewPanLeft()

    @withMdiWidget(DrawingView)
    def viewPanRight(self : Self, view : DrawingView) -> None:
        view.viewPanRight()

    @withMdiWidgetCheckable(DrawingView, "viewGridDisplay")
    def viewGridDisplay(self : Self, view : DrawingView, checked : bool) -> None:
        view.viewGridDisplay(checked)

    @withMdiWidgetCheckable(DrawingView, "viewGridSnap")
    def viewGridSnap(self : Self, view : DrawingView, checked : bool) -> None:
        view.viewGridSnap(checked)

    @withMdiWidget(DrawingView)
    def viewThemeDark(self : Self, view : DrawingView) -> None:
        settings().set("display/theme", "dark")
        view.scene().update()

    @withMdiWidget(DrawingView)
    def viewThemeLightMono(self : Self, view : DrawingView) -> None:
        settings().set("display/theme", "light_mono")
        view.scene().update()

    @withMdiWidget(DrawingView)
    def placePort(self : Self, view : DiagramView) -> None:
        view.placePort()

    @withMdiWidget(DrawingView)
    def placeGate(self : Self, view : DrawingView) -> None:
        view.placeGate()

    @withMdiWidget(DrawingView)
    def placeBlock(self : Self, view : DiagramView) -> None:
        view.placeBlock()

    @withMdiWidget(DrawingView)
    def placeBlockPin(self : Self, view : DiagramView) -> None:
        view.placeBlockPin()

    @withMdiWidget(SymbolView)
    def placeSymbolPin(self : Self, view : SymbolView) -> None:
        view.placeSymbolPin()

    @withMdiWidget(DrawingView)
    def placeConnection(self : Self, view : DiagramView) -> None:
        view.placeConnection()

    @withMdiWidget(DrawingView)
    def placeTap(self : Self, view : DrawingView) -> None:
        view.placeTap()

    @withMdiWidget(DrawingView)
    def placeNetLabel(self : Self, view : DrawingView) -> None:
        view.placeNetLabel()

    @withMdiWidget(DrawingView)
    def placeLine(self : Self, view : DrawingView) -> None:
        view.placeLine()

    @withMdiWidget(DrawingView)
    def placeRectangle(self : Self, view : DrawingView) -> None:
        view.placeRectangle()

    @withMdiWidget(DrawingView)
    def placeEllipse(self : Self, view : DrawingView) -> None:
        view.placeEllipse()

    @withMdiWidget(DrawingView)
    def placePolyline(self : Self, view : DrawingView) -> None:
        view.placePolyline()

    @withMdiWidget(DrawingView)
    def placeText(self : Self, view : DrawingView) -> None:
        view.placeText()

    def windowNavigator(self : Self) -> None:
        window().navigatorDock().show()
        window().navigatorDock().raise_()

    def windowMessages(self : Self) -> None:
        window().messagesDock().show()
        window().messagesDock().raise_()

    def windowTranscript(self : Self) -> None:
        window().transcriptDock().show()
        window().transcriptDock().raise_()

    def windowLog(self : Self) -> None:
        window().logDock().show()
        window().logDock().raise_()

    def aiSettings(self : Self) -> None:
        from ....widgets.dialogs.ai_profiles import AiProfilesDialog
        dialog = AiProfilesDialog(window())
        if not dialog.exec():
            return
        manager = window().aiChatManager()
        if manager is not None:
            manager.refreshChatTitles()
            manager.refreshChatWidgets()
        window().menuBar().updateAiMenu()

    def windowNext(self : Self) -> None:
        window().mdiArea().nextSubWindow()

    def windowPrevious(self : Self) -> None:
        window().mdiArea().previousSubWindow()

    def helpAbout(self : Self) -> None:
        QMessageBox.about(window(), "About", APP_NAME)

