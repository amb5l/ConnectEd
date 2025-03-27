from PyQt6.QtCore    import QAbstractItemModel
from PyQt6.QtWidgets import QTreeView, QWidget
from PyQt6.QtGui     import QFont, QShortcut, QKeySequence


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

