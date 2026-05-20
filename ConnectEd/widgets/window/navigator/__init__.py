from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget

from ....app import model, window

from ..tree_view import TreeView, TreeViewDock

from .overrides import NavigatorOverridesMixin
from .api       import NavigatorApiMixin
from .menus     import NavigatorMenusMixin
from .private   import NavigatorPrivateMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....core.db import Node


class Navigator(
    NavigatorOverridesMixin,
    NavigatorApiMixin,
    NavigatorMenusMixin,
    NavigatorPrivateMixin,
    TreeView
):

    _focus_in : bool

    def __init__(self : Self, parent : QWidget) -> None:
        super().__init__(model(), parent)
        self.header().setVisible(False)
        model().itemChanged.connect(self.onItemChanged)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self.setEditTriggers(self.EditTrigger.EditKeyPressed)
        self._focus_in = False
        self._initMenus()

    def onItemChanged(self : Self, node : "Node") -> None:
        """Handle changes to items in the model, such as renaming."""
        scene = node.scene() if hasattr(node, "scene") else None
        if scene:
            scene.setName(node.text())
        window().mdiArea().update()


class NavigatorDock(TreeViewDock):
    WINDOW_TITLE = "Navigator"

    navigator : Navigator

    def __init__(self : Self, parent : QWidget) -> None:
        super().__init__(None, parent)
        self.navigator = Navigator(self)
        self.setWidget(self.navigator)
