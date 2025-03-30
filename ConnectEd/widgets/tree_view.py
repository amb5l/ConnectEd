from PyQt6.QtCore    import QAbstractItemModel
from PyQt6.QtWidgets import QTreeView, QWidget
from PyQt6.QtGui     import QFont, QShortcut, QKeySequence


class TreeView(QTreeView):
    currentFontSize : int

    def __init__(
        self : 'TreeView',
        parent : QWidget,
        model  : QAbstractItemModel
    ) -> None:
        super().__init__(parent)
        self.setModel(model)
        self.header().setVisible(False)
        self.setFontSize(10) # TODO get from settings
        self.expandAll()
        self.increaseFontShortcut = QShortcut(QKeySequence("Ctrl+="), self)
        self.increaseFontShortcut.activated.connect(self.increaseFontSize)
        self.decreaseFontShortcut = QShortcut(QKeySequence("Ctrl+-"), self)
        self.decreaseFontShortcut.activated.connect(self.decreaseFontSize)

    def setFontSize(self, size: int) -> None:
        """Set the font size for all items in the tree."""
        font = QFont()
        font.setPointSize(size)
        self.setFont(font)
        self.current_font_size = size

    def increaseFontSize(self) -> None:
        """Increase the font size."""
        self.setFontSize(min(self.current_font_size + 1, 20)) # TODO: max from settings

    def decreaseFontSize(self) -> None:
        """Decrease the font size."""
        self.setFontSize(max(self.current_font_size - 1, 6)) # TODO: min from settings

