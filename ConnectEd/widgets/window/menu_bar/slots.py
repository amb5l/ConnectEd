from __future__ import annotations

import functools

from types import UnionType

from typing          import Self, TypeVar, cast
from collections.abc import Callable

from PyQt6.QtWidgets import QMdiSubWindow, QMessageBox

from ....app import logger, settings, window

from ....core.check import checked
from ....core.defs  import APP_NAME

from ....widgets.window.navigator import Navigator

from ....widgets.graphics.views.diagram import DiagramView
from ....widgets.graphics.views.symbol  import SymbolView

from ..sub_window import DocSubWindow


T = TypeVar("T")


def withFocusWidget(
    widget_type : type[T] | UnionType,
) -> Callable[[Callable[["Slots", T], None]], Callable[["Slots"], None]]:
    """
    Decorator that gets the current widget from the focus widget and checks if it's
    of the specified type or a subclass of it before calling the decorated method.

    ``widget_type`` may be a single class or a PEP 604 union (e.g.
    ``DiagramView | Navigator``).
    """
    def decorator(func: Callable[["Slots", T], None]) -> Callable[["Slots"], None]:
        @functools.wraps(func)
        def wrapper(self : Slots) -> None:
            if (current_widget := window().focusWidget()) is None:
                return
            if isinstance(current_widget, widget_type):
                func(self, cast(T, current_widget))
            else:
                raise ValueError(f"{current_widget} is not a {widget_type} or subclass")
        return wrapper
    return decorator


def withMdiSubWindow(
    func : Callable[[Slots, DocSubWindow], None],
) -> Callable[[Slots], None]:
    """
    Decorator that gets the active subwindow from the MDI area and checks
    that it is a ``SubWindow`` before calling the decorated method.
    """
    @functools.wraps(func)
    def wrapper(self : Slots) -> None:
        if (current_subwindow := window().mdiArea().activeSubWindow()) is None:
            return
        if not isinstance(current_subwindow, DocSubWindow):
            logger().error("Current subwindow is not a DocSubWindow")
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
        def wrapper(self : Slots) -> None:
            if (current_subwindow := window().mdiArea().currentSubWindow()) is None:
                return
            if isinstance(current_widget := current_subwindow.widget(), widget_type):
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
        def wrapper(self : Slots) -> None:
            if (current_subwindow := window().mdiArea().currentSubWindow()) is None:
                return
            if isinstance(current_widget := current_subwindow.widget(), widget_type):
                checked = getattr(window().actions, action_name).isChecked()
                # Cast to T since we know it"s a subclass
                func(self, cast(T, current_widget), checked)
            else:
                raise ValueError(f"{current_widget} is not a {widget_type} or subclass")
        return wrapper
    return decorator

class Slots:
    @checked
    def __init__(self : Self) -> None:
        pass

    def fileNew(self : Self) -> None:
        if (navigator := window().navigator()) is None:
            return
        navigator.fileNew()

    def fileOpen(self : Self) -> None:
        if (navigator := window().navigator()) is None:
            return
        navigator.fileOpen()

    @withMdiSubWindow
    def fileSave(self : Self, subwindow : QMdiSubWindow) -> None:
        if (navigator := window().navigator()) is None:
            return
        if isinstance(subwindow, DocSubWindow):
            navigator.fileSave(subwindow)
        else:
            logger().error("Subwindow is not a DocSubWindow")

    @withMdiSubWindow
    def fileSaveAs(self : Self, subwindow : QMdiSubWindow) -> None:
        if (navigator := window().navigator()) is None:
            return
        if isinstance(subwindow, DocSubWindow):
            navigator.fileSaveAs(subwindow)
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

    @withMdiWidget(DiagramView)
    def editCancel(self : Self, view : DiagramView) -> None:
        view.editCancel()

    @withMdiWidget(DiagramView)
    def editUndo(self : Self, view : DiagramView) -> None:
        view.editUndo()

    @withMdiWidget(DiagramView)
    def editRedo(self : Self, view : DiagramView) -> None:
        view.editRedo()

    @withMdiWidget(DiagramView)
    def editCut(self : Self, view : DiagramView) -> None:
        view.editCut()

    @withFocusWidget(DiagramView | Navigator)
    def editCopy(self : Self, widget : DiagramView | Navigator) -> None:
        widget.editCopy()

    @withFocusWidget(DiagramView | Navigator)
    def editPaste(self : Self, widget : DiagramView | Navigator) -> None:
        widget.editPaste()

    @withMdiWidget(DiagramView)
    def editDelete(self : Self, view : DiagramView) -> None:
        view.editDelete()

    @withMdiWidget(DiagramView)
    def editDuplicate(self : Self, view : DiagramView) -> None:
        view.editDuplicate()

    @withMdiWidget(DiagramView)
    def editSelectArea(self : Self, view : DiagramView) -> None:
        view.editSelectArea()

    @withMdiWidget(DiagramView)
    def editSelectAll(self : Self, view : DiagramView) -> None:
        view.editSelectAll()

    @withMdiWidget(DiagramView)
    def editRotateCW(self : Self, view : DiagramView) -> None:
        view.editRotateCW()

    @withMdiWidget(DiagramView)
    def editRotateCCW(self : Self, view : DiagramView) -> None:
        view.editRotateCCW()

    @withMdiWidget(DiagramView)
    def editProperties(self : Self, view : DiagramView) -> None:
        view.editItemProperties()

    @withMdiWidget(DiagramView)
    def editAppearance(self : Self, view : DiagramView) -> None:
        view.editAppearance()

    @withMdiWidget(DiagramView)
    def editQuery(self : Self, view : DiagramView) -> None:
        view.editQuery()

    @withMdiWidget(DiagramView)
    def viewZoomAll(self : Self, view : DiagramView) -> None:
        view.viewZoomAll()

    @withMdiWidget(DiagramView)
    def viewZoomSheet(self : Self, view : DiagramView) -> None:
        view.viewZoomSheet()

    @withMdiWidget(DiagramView)
    def viewZoomArea(self : Self, view : DiagramView) -> None:
        view.viewZoomArea()

    @withMdiWidget(DiagramView)
    def viewZoomIn(self : Self, view : DiagramView) -> None:
        view.viewZoomIn()

    @withMdiWidget(DiagramView)
    def viewZoomOut(self : Self, view : DiagramView) -> None:
        view.viewZoomOut()

    @withMdiWidget(DiagramView)
    def viewPan(self : Self, view : DiagramView) -> None:
        view.viewPan()

    @withMdiWidget(DiagramView)
    def viewPanUp(self : Self, view : DiagramView) -> None:
        view.viewPanUp()

    @withMdiWidget(DiagramView)
    def viewPanDown(self : Self, view : DiagramView) -> None:
        view.viewPanDown()

    @withMdiWidget(DiagramView)
    def viewPanLeft(self : Self, view : DiagramView) -> None:
        view.viewPanLeft()

    @withMdiWidget(DiagramView)
    def viewPanRight(self : Self, view : DiagramView) -> None:
        view.viewPanRight()

    @withMdiWidgetCheckable(DiagramView, "viewGridDisplay")
    def viewGridDisplay(self : Self, view : DiagramView, checked : bool) -> None:
        view.viewGridDisplay(checked)

    @withMdiWidgetCheckable(DiagramView, "viewGridSnap")
    def viewGridSnap(self : Self, view : DiagramView, checked : bool) -> None:
        view.viewGridSnap(checked)

    @withMdiWidget(DiagramView)
    def viewThemeDark(self : Self, view : DiagramView) -> None:
        settings().set("display/theme", "dark")
        if (scene := view.scene()) is not None:
            scene.update()

    @withMdiWidget(DiagramView)
    def viewThemeLightMono(self : Self, view : DiagramView) -> None:
        settings().set("display/theme", "light_mono")
        if (scene := view.scene()) is not None:
            scene.update()

    @withMdiWidget(DiagramView)
    def placePort(self : Self, view : DiagramView) -> None:
        view.placePort()

    @withMdiWidget(DiagramView)
    def placeGate(self : Self, view : DiagramView) -> None:
        view.placeGate()

    @withMdiWidget(DiagramView)
    def placeBlock(self : Self, view : DiagramView) -> None:
        view.placeBlock()

    @withMdiWidget(DiagramView)
    def placeBlockPin(self : Self, view : DiagramView) -> None:
        view.placeBlockPin()

    @withMdiWidget(SymbolView)
    def placeSymbolPin(self : Self, view : SymbolView) -> None:
        view.placeSymbolPin()

    @withMdiWidget(DiagramView)
    def placeConnection(self : Self, view : DiagramView) -> None:
        view.placeConnection()

    @withMdiWidget(DiagramView)
    def placeTap(self : Self, view : DiagramView) -> None:
        view.placeTap()

    @withMdiWidget(DiagramView)
    def placeNetLabel(self : Self, view : DiagramView) -> None:
        view.placeNetLabel()

    @withMdiWidget(DiagramView)
    def placeLine(self : Self, view : DiagramView) -> None:
        view.placeLine()

    @withMdiWidget(DiagramView)
    def placeRectangle(self : Self, view : DiagramView) -> None:
        view.placeRectangle()

    @withMdiWidget(DiagramView)
    def placeEllipse(self : Self, view : DiagramView) -> None:
        view.placeEllipse()

    @withMdiWidget(DiagramView)
    def placePolyline(self : Self, view : DiagramView) -> None:
        view.placePolyline()

    @withMdiWidget(DiagramView)
    def placeText(self : Self, view : DiagramView) -> None:
        view.placeText()

    def windowNavigator(self : Self) -> None:
        if (navigator_dock := window().navigatorDock()) is not None:
            navigator_dock.show()
            navigator_dock.raise_()
        else:
            logger().error("No navigator dock")

    def windowMessages(self : Self) -> None:
        if (messages_dock := window().messagesDock()) is not None:
            messages_dock.show()
            messages_dock.raise_()
        else:
            logger().error("No messages dock")

    def windowTranscript(self : Self) -> None:
        if (transcript_dock := window().transcriptDock()) is not None:
            transcript_dock.show()
            transcript_dock.raise_()
        else:
            logger().error("No transcript dock")

    def windowLog(self : Self) -> None:
        if (log_dock := window().logDock()) is not None:
            log_dock.show()
            log_dock.raise_()
        else:
            logger().error("No log dock")

    def aiSettings(self : Self) -> None:
        from ....widgets.dialogs.ai_profiles import AiProfilesDialog
        dialog = AiProfilesDialog(window())
        if not dialog.exec():
            return
        if (manager := window().aiChatManager()) is not None:
            manager.refreshChatTitles()
            manager.refreshChatWidgets()
        if (menu_bar := window().menuBar()) is not None:
            menu_bar.updateAiMenu()
        else:
            logger().error("No menu bar")

    def windowNext(self : Self) -> None:
        window().mdiArea().nextSubWindow()

    def windowPrevious(self : Self) -> None:
        window().mdiArea().previousSubWindow()

    def helpAbout(self : Self) -> None:
        QMessageBox.about(window(), "About", APP_NAME)

