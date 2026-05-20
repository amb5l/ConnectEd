from PyQt6.QtCore import QPointF, QSizeF

import ConnectEd.scripting as cs


def test(app : cs.ConnectEdApp):

    print("test started")

    # get model (so we can work with designs)
    model = app.model()
    # get window (so we can drive the GUI)
    window = app.window()
    # get menu bar
    menu_bar = window.menuBar()
    # get menus
    menus = menu_bar.menusDict()
    # get file menu
    file_menu = menus["File"]
    # get file - new submenu
    file_new_menu = file_menu.subMenusDict()["New"]
    # get file - new - design action
    file_new_design_action = file_new_menu.actionsDict()["Design"]
    # trigger the action to create a new design
    file_new_design_action.trigger()
    # get all design items
    design_db_nodes = model.designDbNodes()
    # pick the first design item
    design_db_node = design_db_nodes[0]
    # get all diagram items in the design
    diagram_nodes = design_db_node.diagramNodes()
    # pick the first diagram item
    diagram_node = diagram_nodes[0]
    # get all views for the diagram item
    views = diagram_node.views()
    # pick the first view
    view = views[0]
    # zoom to fit all the diagram contents
    view.viewZoomAll()
    # create a rectangle
    pos = QPointF(100, 100)
    size = QSizeF(100, 100)
    view.placeRectangle()
    view.mouseLeftClick(pos)
    view.mouseLeftClick(QPointF(pos.x() + size.width(), pos.y() + size.height()))

    # done
    print("test finished")

# run test (no splash screen)
cs.run(test, ["--nosplash"])
