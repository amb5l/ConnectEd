from typing import Self

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui     import QStandardItemModel

from ...graphics.scenes.diagram import DiagramScene

from ..tree_view import TreeView, TreeViewDock


class NetlistBrowser(TreeView):

    _diagram : DiagramScene | None
    _model   : QStandardItemModel

    def __init__(self : Self, parent : QWidget) -> None:
        self._initModel()
        super().__init__(self._model, parent)

    def update(self : Self) -> None:
        # rebuild model from netlist
        pass

    def _initModel(self : Self) -> None:
        self._model = QStandardItemModel()
        self._model.setHorizontalHeaderLabels(["Name", "Suffix", "Type"])


class NetlistBrowserDock(TreeViewDock):
    WINDOW_TITLE = "Netlist"

    _browser : NetlistBrowser

    def __init__(self : Self, parent : QWidget) -> None:
        super().__init__(None, parent)
        self._browser = NetlistBrowser(self)
        self.setWidget(self._browser)
