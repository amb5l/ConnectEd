from PyQt6.QtCore    import QAbstractItemModel, Qt
from PyQt6.QtWidgets import QTreeView, QWidget, QMenu
from PyQt6.QtGui     import QFont, QShortcut, QKeySequence, QAction

from ..core import Design
from .. import hub


class TreeView(QTreeView):
    def __init__(
        self : 'TreeView',
        parent : QWidget,
        model  : QAbstractItemModel
    ) -> None:
        super().__init__(parent)
        self.setModel(model)
        self.header().setVisible(False)
        self.set_font_size(10) # TODO get from settings
        self.expandAll()
        self.increase_font_shortcut = QShortcut(QKeySequence("Ctrl++"), self)
        self.increase_font_shortcut.activated.connect(self.increase_font_size)
        self.decrease_font_shortcut = QShortcut(QKeySequence("Ctrl+-"), self)
        self.decrease_font_shortcut.activated.connect(self.decrease_font_size)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def set_font_size(self, size: int) -> None:
        """Set the font size for all items in the tree."""
        font = QFont()
        font.setPointSize(size)
        self.setFont(font)
        self.current_font_size = size

    def increase_font_size(self) -> None:
        """Increase the font size."""
        self.set_font_size(self.current_font_size + 1)

    def decrease_font_size(self) -> None:
        """Decrease the font size."""
        self.set_font_size(max(self.current_font_size - 1, 1))

    def show_context_menu(self, pos):
        """Handle right-click context menu."""
        index = self.indexAt(pos)
        if not index.isValid():
            return
        item = self.model().itemFromIndex(index)
        if item.text() == "Designs":  # Check if the clicked item is "Designs"
            menu = QMenu(self)
            new_design_action = QAction("New Design", self)
            new_design_action.triggered.connect(self.create_new_design)
            menu.addAction(new_design_action)
            menu.exec(self.viewport().mapToGlobal(pos))

    def create_new_design(self):
        """Create a new Design via DatabaseManager."""
        hub.database_manager.new(Design)
