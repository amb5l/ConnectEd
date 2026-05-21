"""DrawingView rectangle placement via QTest mouse delivery."""

from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QMdiSubWindow

from ConnectEd.app import app, settings
from ConnectEd.scripting import Window, gui
from ConnectEd.widgets.graphics.items.rectangle import RectangleItem
from ConnectEd.widgets.graphics.views.diagram import DiagramView


def _activeDiagramView(driver) -> DiagramView:
    win = driver.window()
    mdi = win.mdiArea()
    assert mdi is not None
    sub = mdi.activeSubWindow()
    assert sub is not None, "no active MDI subwindow after File → New → Design"
    view = sub.widget()
    assert isinstance(view, DiagramView), (
        f"expected DiagramView, got {type(view).__name__}"
    )
    return view


def validateDrawingRectangle(window : Window) -> None:
    driver = gui(window)
    connected_bar = window.menuBar()
    assert connected_bar is not None

    file_menu = connected_bar.getMenus()["File"]
    new_menu = file_menu.getSubMenus()["New"]
    design = new_menu.getAction("Design")
    assert design is not None
    design.trigger()
    driver.processEvents()

    assert app().model().designDbNodes(), "no design after File → New → Design"
    assert app().model().designDbNodes()[0].scene() is not None

    view = _activeDiagramView(driver)
    sub = driver.window().mdiArea().activeSubWindow()
    assert isinstance(sub, QMdiSubWindow)
    driver.window().mdiArea().activateSubWindow(sub)
    view.setFocus()
    driver.processEvents()
    view.ui.viewZoomAll()
    driver.processEvents()

    view.ui.placeRectangle()
    driver.processEvents()

    pos1 = QPointF(100.0, 100.0)
    pos2 = QPointF(250.0, 250.0)
    p1 = driver.viewPos(view, pos1)
    p2 = driver.viewPos(view, pos2)
    drag = settings().get("prefs/mouse/drag") or 5
    assert (p2 - p1).manhattanLength() > drag, "mouse drag must exceed prefs/mouse/drag"

    driver.mouseDrag(view, p1, p2)
    driver.processEvents()

    scene = view.scene()
    assert scene is not None
    rectangles = [i for i in scene.items() if isinstance(i, RectangleItem)]
    assert rectangles, "expected RectangleItem on scene after QTest drag"
