from typing import Self

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui     import QStandardItem, QStandardItemModel

from ...graphics.scenes.diagram import DiagramScene

from ..tree_view import TreeView, TreeViewDock


_HEADERS = ["Name", "Suffix", "Type"]


class NetlistBrowser(TreeView):

    _diagram : DiagramScene | None
    _model   : QStandardItemModel

    def __init__(self : Self, parent : QWidget) -> None:
        self._diagram = None
        self._model = QStandardItemModel()
        self._model.setHorizontalHeaderLabels(_HEADERS)
        super().__init__(self._model, parent)

    def setDiagram(self : Self, diagram : DiagramScene | None) -> None:
        if self._diagram is not None:
            try:
                self._diagram.netlistChanged.disconnect(self.refresh)
            except TypeError:
                pass
        self._diagram = diagram
        if self._diagram is not None:
            self._diagram.netlistChanged.connect(self.refresh)
        self.refresh()

    def refresh(self : Self) -> None:
        # rebuild model from netlist
        self._model.clear()
        self._model.setHorizontalHeaderLabels(_HEADERS)
        if self._diagram is None:
            return
        # sort nets: resolved (str-keyed) first by name, then unresolved
        # (int-keyed) by subnet id.
        nets_u = self._diagram.netlist.nets()
        net_keys = sorted(
            nets_u.keys(),
            key=lambda k: (isinstance(k, int), str(k))
        )
        # append rows to model
        subnets_by_id = self._diagram.netlist.subnets()
        for net_key in net_keys:
            net = nets_u[net_key]
            net_name = str(net_key)
            net_item = self._appendRow(self._model, net_name, net.suffix, "?")
            # subnet sorting:
            # ranges, then indices, then scalars
            # TODO
            for subnet_id in net.subnets:
                subnet = subnets_by_id[subnet_id]
                subnet_label = \
                    str(subnet.id) if subnet.name is None else subnet.name
                subnet_item = self._appendRow(
                    net_item, subnet_label, subnet.suffix, "?"
                )
                for node in subnet.nodes:
                    node_name, node_suffix, node_type = \
                        self._diagram.netlist.nodeNameSuffixType(node)
                    self._appendRow(
                        subnet_item, node_name, node_suffix, node_type
                    )
        self.expandAll()

    @staticmethod
    def _appendRow(
        parent : QStandardItem | QStandardItemModel,
        name   : str | None,
        suffix : str | None,
        type_  : str,
    ) -> QStandardItem:
        row = [
            QStandardItem(name   or ""),
            QStandardItem(suffix or ""),
            QStandardItem(type_),
        ]
        for item in row:
            item.setEditable(False)
        parent.appendRow(row)
        return row[0]


class NetlistBrowserDock(TreeViewDock):
    WINDOW_TITLE = "Netlist"

    _browser : NetlistBrowser

    def __init__(self : Self, parent : QWidget) -> None:
        super().__init__(None, parent)
        self._browser = NetlistBrowser(self)
        self.setWidget(self._browser)
