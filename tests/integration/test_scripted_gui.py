from PyQt6.QtCore import QPointF, QSizeF

import ConnectEd.scripting as cs

from ConnectEd.widgets.graphics.items import DEFAULT

from ConnectEd.widgets.graphics.items.rectangle import Rectangle


def test(app : cs.ConnectEdApp):

    print("test started")

    assert isinstance(app, cs.ConnectEdApp)

    # verify we are running in GUI mode
    assert app.cli() == False

    # get main window
    window = app.window()
    assert window is not None
    assert window.isVisible()

    # verify existence and visibility of menu bar, dock widgets, and MDI area
    menu_bar = window.menu_bar
    assert menu_bar is not None
    assert menu_bar.isHidden() == False
    explorer_dock = window.explorer_dock
    assert explorer_dock is not None
    assert explorer_dock.isHidden() == False
    messages_viewer = window.messages_viewer
    assert messages_viewer is not None
    assert messages_viewer.isHidden() == False
    transcript_viewer = window.transcript_viewer
    assert transcript_viewer is not None
    assert transcript_viewer.isHidden() == False
    log_viewer = window.log_viewer
    assert log_viewer is not None
    assert log_viewer.isHidden() == False
    mdi_area = window.mdi_area
    assert mdi_area is not None
    assert mdi_area.isHidden() == False

    # verify existence of File menu and submenus
    menus = menu_bar.menusDict()
    assert "File"   in menus.keys()
    file_menu = menus["File"]
    assert file_menu is not None
    file_new_menu = file_menu.subMenusDict()["New"]
    assert file_new_menu is not None

    # verify existence of Edit menu
    assert "Edit"   in menus.keys()
    file_new_menu = file_menu.subMenusDict()["New"]
    edit_menu = menus["Edit"]
    assert edit_menu is not None
    edit_actions = edit_menu.actionsDict()

    # verify existence of View menu and submenus
    assert "View"   in menus.keys()
    view_menu = menus["View"]
    assert view_menu is not None
    view_theme_menu = view_menu.subMenusDict()["Theme"]
    assert view_theme_menu is not None

    # verify existence of Place menu
    assert "Place"  in menus.keys()
    place_menu = menus["Place"]
    assert place_menu is not None

    # verify existence of Window menu
    assert "Window" in menus.keys()
    window_menu = menus["Window"]
    assert window_menu is not None

    # verify existence of Help menu
    assert "Help"   in menus.keys()
    help_menu = menus["Help"]
    assert help_menu is not None

    # verify existence of File menu and submenu actions
    file_actions = file_menu.actionsDict()
    assert "Open"         in file_actions
    assert "Save"         in file_actions
    assert "Save As"      in file_actions
    assert "Exit"         in file_actions
    file_new_actions = file_new_menu.actionsDict()
    assert "Design"   in file_new_actions
    assert "Library"  in file_new_actions

    # verify existence of Edit menu actions
    edit_actions = edit_menu.actionsDict()
    assert "Undo"         in edit_actions
    assert "Redo"         in edit_actions
    assert "Cut"          in edit_actions
    assert "Copy"         in edit_actions
    assert "Paste"        in edit_actions
    assert "Delete"       in edit_actions
    assert "Duplicate"    in edit_actions
    assert "Select Area"  in edit_actions
    assert "Select All"   in edit_actions
    assert "Properties"   in edit_actions
    assert "Appearance"   in edit_actions
    assert "Query"        in edit_actions

    # verify existence of View menu and submenu actions
    view_actions = view_menu.actionsDict()
    assert "Zoom All"      in view_actions
    assert "Zoom Sheet"    in view_actions
    assert "Zoom Area"     in view_actions
    assert "Zoom In"       in view_actions
    assert "Zoom Out"      in view_actions
    view_theme_actions = view_theme_menu.actionsDict()
    assert "Dark"         in view_theme_actions
    assert "Light Mono"   in view_theme_actions

    # verify existence of Place menu actions
    place_actions = place_menu.actionsDict()
    assert "Port"         in place_actions
    assert "Block"        in place_actions
    assert "Block Pin"    in place_actions
    assert "Rectangle"    in place_actions
    assert "Text Block"   in place_actions

    # verify existence of Window menu actions
    window_actions = window_menu.actionsDict()
    assert "Explorer"     in window_actions
    assert "Messages"     in window_actions
    assert "Transcript"   in window_actions
    assert "Log"          in window_actions

    # verify existence of Help menu actions
    help_actions = help_menu.actionsDict()
    assert "About"        in help_actions

    # get model
    model = app.model()
    assert model is not None

    # create a new design
    file_new_design_action = file_new_menu.actionsDict()["Design"]
    file_new_design_action.trigger()

    # verify newly created design
    design_items = model.designItems()
    assert len(design_items) == 1
    design_item = design_items[0]
    assert design_item is not None
    assert design_item.text() == "UntitledDesign1"
    diagram_items = design_item.diagramItems()
    assert len(diagram_items) == 1
    diagram_item = diagram_items[0]
    assert diagram_item is not None
    assert diagram_item.text() == "UntitledDiagram1"
    symbol_items = design_item.symbolItems()
    assert len(symbol_items) == 0

    # get view of design diagram and verify it
    views = diagram_item.views()
    assert len(views) == 1
    view = views[0]
    assert view is not None
    view_window = view.window()
    assert view_window is not None
    assert view_window.isVisible()
    assert view_window.isEnabled()
    assert view_window.isActiveWindow()

    # start view interaction
    view.viewZoomAll()

    # create a rectangle
    pos = QPointF(100, 100)
    size = QSizeF(100, 100)
    view.placeRectangle()
    view.mouseLeftClick(pos)
    view.mouseLeftClick(QPointF(pos.x() + size.width(), pos.y() + size.height()))
    # verify existence and basic properties
    rect = view.scene().items()[0]
    assert isinstance(rect, Rectangle), \
        f"Got {type(rect)}, expected {Rectangle}"
    assert rect.pos() == pos, \
        f"Got {rect.pos()}, expected {pos}"
    assert rect.rect().width() == size.width(), \
        f"Got {rect.rect().width()}, expected {size.width()}"
    assert rect.rect().height() == size.height(), \
        f"Got {rect.rect().height()}, expected {size.height()}"
    assert rect.line.getColor() == DEFAULT, \
        f"Got {rect.line.getColor()}, expected {DEFAULT}"
    assert rect.line.getWidth() == DEFAULT, \
        f"Got {rect.line.getWidth()}, expected {DEFAULT}"
    assert rect.line.getStyle() == DEFAULT, \
        f"Got {rect.line.getStyle()}, expected {DEFAULT}"
    assert rect.line.getStyle() == DEFAULT
     # verify selected and unselected appearance
    defaults = app.settings().get("theme/elements/Rectangle")
    assert rect.isSelected(), \
        f"Got {rect.isSelected()}, expected True"
    rect_pen = rect.pen()
    assert rect_pen.color() == app.settings().get("theme/selected").line, \
        f"Got {rect_pen.color()}, expected {app.settings().get("theme/selected").line}"
    assert rect_pen.width() == defaults.line.width, \
        f"Got {rect_pen.width()}, expected {defaults.line.width}"
    assert rect_pen.style() == defaults.line.style, \
        f"Got {rect_pen.style()}, expected {defaults.line.style}"
    assert rect_pen.style() == defaults.line.style
    rect.setSelected(False)
    rect_pen = rect.pen()
    assert rect_pen.color() == defaults.line.color, \
        f"Got {rect_pen.color()}, expected {defaults.line.color}"
    assert rect_pen.width() == defaults.line.width, \
        f"Got {rect_pen.width()}, expected {defaults.line.width}"
    assert rect_pen.style() == defaults.line.style, \
        f"Got {rect_pen.style()}, expected {defaults.line.style}"
    assert rect_pen.style() == defaults.line.style

    # done
    print("test finished")


class TestScriptedGUI:
    def test_scripted_gui(self):
        cs.run(test, ["--nosplash"])


if __name__ == "__main__":
    cs.run(test, ["--nosplash"])
    #cs.run(test)
