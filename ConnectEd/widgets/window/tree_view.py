from typing import Self

from PyQt6.QtCore    import QAbstractItemModel
from PyQt6.QtWidgets import QTreeView, QWidget, QDockWidget
from PyQt6.QtGui     import QFont, QShortcut, QKeySequence

from ...app       import settings
from ...resources import getIconPath


class TreeView(QTreeView):
    current_font_size : int

    def __init__(
        self   : Self,
        model  : QAbstractItemModel,
        parent : QWidget
    ) -> None:
        super().__init__(parent)
        self.setModel(model)
        self.setFontSize(settings().get("display/font_size"))
        self.customizeAppearance()
        self.expandAll()
        self.increaseFontShortcut = QShortcut(QKeySequence("Ctrl+="), self)
        self.increaseFontShortcut.activated.connect(self.increaseFontSize)
        self.decreaseFontShortcut = QShortcut(QKeySequence("Ctrl+-"), self)
        self.decreaseFontShortcut.activated.connect(self.decreaseFontSize)

    def customizeAppearance(self : Self) -> None:
        if settings().get("display/theme") == "dark":
            self.setStyleSheet("""
                QTreeView::branch {
                    image: none;
                }
                QTreeView::branch:has-children:closed {
                    image: url(""" + getIconPath("expand_bright.svg").replace("\\", "/") + """);
                }
                QTreeView::branch:has-children:open {
                    image: url(""" + getIconPath("collapse_bright.svg").replace("\\", "/") + """);
                }
                QTreeView::branch:hover {
                    background-color: rgba(255, 255, 255, 50);
                }
            """)

    def setFontSize(self : Self, size : int) -> None:
        """Set the font size for all items in the tree."""
        font = QFont()
        font.setPointSizeF(size)
        self.setFont(font)
        self.current_font_size = size

    def increaseFontSize(self : Self) -> None:
        """Increase the font size."""
        self.setFontSize(min(self.current_font_size + 1, 20)) # TODO: max from settings

    def decreaseFontSize(self : Self) -> None:
        """Decrease the font size."""
        self.setFontSize(max(self.current_font_size - 1, 6)) # TODO: min from settings

class TreeViewDock(QDockWidget):
    WINDOW_TITLE = "Tree Viewer"

    def __init__(
        self   : Self,
        widget : TreeView | None,
        parent : QWidget
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(self.WINDOW_TITLE)
        if widget is not None:
            self.setWidget(widget)
