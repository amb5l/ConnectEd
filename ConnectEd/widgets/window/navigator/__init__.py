from typing      import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui     import QStandardItemModel, QStandardItem

from ....app import session

from ....core.doc import Doc, NavItemSpec, DocBinding

from ..tree_view import TreeView, TreeViewDock

from .api import NavigatorApiMixin


class NavItem(QStandardItem):
    pass


class NavModel(QStandardItemModel):
    pass


class Navigator(NavigatorApiMixin, TreeView):
    """Navigator widget. A UI for Session."""

    _model    : NavModel
    _groups   : dict[str, NavItem]

    def __init__(self : Self, parent : QWidget) -> None:
        # create an empty model
        self._model = NavModel()
        # get top group rows from session.docTypes()
        self._groups = {}
        for doc_type in session().docTypes():
            group_name = doc_type.group
            group_item = NavItem(group_name)
            group_item.setFlags(group_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            font = group_item.font()
            font.setBold(True)
            group_item.setFont(font)
            self._model.appendRow(group_item)
            self._groups[group_name] = group_item
        # ensure changes propagate
        self._model.itemChanged.connect(self.onItemChanged)
        # initialise this widget
        super().__init__(self._model, parent)
        self.header().setVisible(False)

    def onItemChanged(self : Self, item : NavItem) -> None:
        """Handle rename on editor rows only."""
        binding : DocBinding | None = \
            item.data(Qt.ItemDataRole.UserRole)
        if binding is None or binding.subject is None:
            return
        binding.doc.navRename(binding.subject, item.text())

    def _addDoc(
        self   : Self,
        parent : NavItem | NavModel,
        doc    : Doc,
        path   : str = ""
    ) -> None:
        def _addRows(
            parent : NavItem,
            specs  : NavItemSpec | list[NavItemSpec]
        ) -> None:
            if not isinstance(specs, list):
                specs = [specs]
            for spec in specs:
                text = spec.subject if isinstance(spec.subject, str) \
                    else spec.subject.name()
                item = NavItem(text)
                if isinstance(spec.subject, str):
                    # static string (typically a container)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                else:
                    item.setData(
                        DocBinding(doc, spec.subject),
                        Qt.ItemDataRole.UserRole,
                    )
                if spec.tip is not None:
                    item.setToolTip(spec.tip)
                parent.appendRow(item)
                if spec.children is not None:
                    _addRows(item, spec.children)
        _addRows(self._model, doc.navItemSpec())


class NavigatorDock(TreeViewDock):
    """Dock for the Navigator widget."""

    WINDOW_TITLE = "Navigator"

    _navigator : Navigator

    def __init__(self : Self, parent : QWidget) -> None:
        super().__init__(None, parent)
        self._navigator = Navigator(self)
        self.setWidget(self._navigator)
