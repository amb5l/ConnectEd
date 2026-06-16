from typing      import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui     import QStandardItemModel, QStandardItem

from ....app import logger, session

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
        """Handle changes to items in the model. Assumption: renaming only."""
        item_binding : DocBinding | None = \
            item.data(Qt.ItemDataRole.UserRole)
        if item_binding is None:
            logger().error(f"NavigatorItem has no UserRole: {item.text()}")
            return
        item_binding.doc.rename(item_binding.widget)

    def _addDoc(
        self   : Self,
        parent : NavItem | NavModel,
        doc    : Doc,
        path   : str = ""
    ) -> None:
        doc_item = NavItem(doc.displayName())
        user_role = DocBinding(doc, None)
        doc_item.setData(user_role, Qt.ItemDataRole.UserRole)
        # add child rows
        def _addChildren(item : NavItem, child_specs : list[NavItemSpec]) -> None:
            for child_spec in child_specs:
                child_item = NavItem(child_spec.label)
                child_user_role = DocBinding(
                    doc, child_spec
                )
                child_item.setData(child_user_role, Qt.ItemDataRole.UserRole)
                item.appendRow(child_item)
                if child_spec.child_specs is not None:
                    _addChildren(child_item, child_spec.child_specs)
        child_specs = doc.navChildSpecs()
        _addChildren(doc_item, child_specs)
        # finalise
        doc_item.setToolTip(path or "(not saved)")
        parent.appendRow(doc_item)


class NavigatorDock(TreeViewDock):
    """Dock for the Navigator widget."""

    WINDOW_TITLE = "Navigator"

    _navigator : Navigator

    def __init__(self : Self, parent : QWidget) -> None:
        super().__init__(None, parent)
        self._navigator = Navigator(self)
        self.setWidget(self._navigator)
