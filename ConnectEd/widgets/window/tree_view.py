from typing import Self

from PyQt6.QtCore    import Qt, QAbstractItemModel
from PyQt6.QtWidgets import QTreeView, QWidget, QDockWidget
from PyQt6.QtGui     import QShortcut, QKeySequence, QWheelEvent

from ...app       import logger, settings

from ...resources import getIconPath

from ...core.check import checked

from ..mixin.ui_font_size import UiFontSizeMixin


class TreeView(UiFontSizeMixin, QTreeView):
    _SETTINGS_UI_PATH = "default"

    @checked
    def __init__(
        self   : Self,
        model  : QAbstractItemModel,
        parent : QWidget
    ) -> None:
        super().__init__(parent)
        self.setModel(model)
        self._customizeAppearance()
        self.initFontSize()
        self.expandAll()
        self.increaseFontShortcut = QShortcut(QKeySequence("Ctrl+="), self)
        self.increaseFontShortcut.activated.connect(self.increaseFontSize)
        self.decreaseFontShortcut = QShortcut(QKeySequence("Ctrl+-"), self)
        self.decreaseFontShortcut.activated.connect(self.decreaseFontSize)

    def wheelEvent(self : Self, a0 : QWheelEvent | None) -> None:
        if a0 is None:
            logger().warning("No event")
            return
        if a0.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if a0.angleDelta().y() > 0:
                self.increaseFontSize()
            elif a0.angleDelta().y() < 0:
                self.decreaseFontSize()
            a0.accept()
            return
        super().wheelEvent(a0)

    def _customizeAppearance(self : Self) -> None:
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


class TreeViewDock(QDockWidget):
    WINDOW_TITLE = "Tree Viewer"

    @checked
    def __init__(
        self   : Self,
        widget : TreeView | None,
        parent : QWidget
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(self.WINDOW_TITLE)
        if widget is not None:
            self.setWidget(widget)
