from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QAbstractItemView

from ....app import session

from ....core.check import checked
from ....core.doc   import Doc

from ..tree_view import TreeView, TreeViewDock

from .types    import NavItem, NavModel
from .delegate import NavItemDelegate
from .private  import NavigatorPrivateMixin
from .events   import NavigatorEventsMixin
from .menu     import NavigatorMenuMixin
from .api      import NavigatorApiMixin


class Navigator(
    NavigatorPrivateMixin,
    NavigatorEventsMixin,
    NavigatorMenuMixin,
    NavigatorApiMixin,
    TreeView
):
    """Navigator widget. A UI for Session."""

    _SETTINGS_UI_PATH = "navigator"

    _model       : NavModel
    _group_items : dict[str, NavItem]

    @checked
    def __init__(self : Self, parent : QWidget) -> None:
        # create an empty model
        self._model = NavModel()
        # get top group rows from session.docTypes()
        self._group_items = {}
        for doc_type in session().docTypes():
            group_name = doc_type.group
            group_item = NavItem(group_name)
            group_item.setFlags(group_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            font = group_item.font()
            font.setBold(True)
            group_item.setFont(font)
            self._model.appendRow(group_item)
            self._group_items[group_name] = group_item
        self._updateGroups()
        # initialise this widget
        super().__init__(self._model, parent)
        if (header := self.header()) is None:
            raise RuntimeError("No header")
        header.setVisible(False)
        self.setItemDelegate(NavItemDelegate(self))
        self.setEditTriggers(QAbstractItemView.EditTrigger.EditKeyPressed)
        # initialise context menus
        self.initMenus()
        # hook up to session
        session().docChanged.connect(self.onDocChanged)
        session().docClosed.connect(self.onDocClosed)

    def onDocChanged(self : Self, doc : Doc) -> None:
        """Handle changes to documents."""
        self._refreshDocNav(doc)

    def onDocClosed(self : Self, doc : Doc) -> None:
        """Remove a closed document from the tree."""
        self._removeDocFromTree(doc)


class NavigatorDock(TreeViewDock):
    """Dock for the Navigator widget."""

    WINDOW_TITLE = "Navigator"

    _navigator : Navigator

    @checked
    def __init__(self : Self, parent : QWidget) -> None:
        super().__init__(None, parent)
        self._navigator = Navigator(self)
        self.setWidget(self._navigator)
