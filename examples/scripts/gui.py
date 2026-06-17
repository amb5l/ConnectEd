from PyQt6.QtCore import QPointF, QSizeF

import ConnectEd.scripting as cs


def test(app : cs.App):

    print("test started")

    model = app.model()
    window = app.window()
    assert window is not None
    driver = cs.gui(window)

    menu_bar = driver.menuBar()
    assert menu_bar is not None
    file_menu = menu_bar.getMenus()["File"]
    file_new_menu = file_menu.getSubMenus()["New"]
    file_new_design_action = file_new_menu.getAction("Design")
    assert file_new_design_action is not None
    file_new_design_action.trigger()
    driver.processEvents()

    design_db_node = model.designDbNodes()[0]
    assert design_db_node.scene() is not None
    mdi = window.mdiArea()
    assert mdi is not None
    sub = mdi.activeSubWindow()
    assert sub is not None
    view = sub.widget()
    assert view is not None
    view.viewZoomAll()
    driver.processEvents()

    pos = QPointF(100, 100)
    size = QSizeF(100, 100)
    view.placeRectangle()
    driver.processEvents()

    p1 = driver.viewPos(view, pos)
    p2 = driver.viewPos(
        view,
        QPointF(pos.x() + size.width(), pos.y() + size.height()),
    )
    driver.mouseDrag(view, p1, p2)

    print("test finished")

cs.run(test, ["--nosplash"])
