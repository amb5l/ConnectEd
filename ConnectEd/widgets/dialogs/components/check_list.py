from __future__ import annotations

from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton
)

from ....core.check import checked


class CheckList(QWidget):
    """
    List of items with checkboxes.
    Left: scrollable list of items with checkboxes.
    Right: buttons - all, none, invert.
    OK button is disabled until at least one item is enabled.
    """

    _items     : list[str]
    _ok_button : QPushButton | None
    _list      : QListWidget

    @checked
    def __init__(
        self      : Self,
        items     : list[str],
        ok_button : QPushButton | None = None
    ) -> None:
        super().__init__()
        self._items     = list(items)
        self._ok_button = ok_button
        layout          = QHBoxLayout(self)
        self._list      = QListWidget()
        for item in items:
            entry = QListWidgetItem(item)
            entry.setFlags(entry.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            entry.setCheckState(Qt.CheckState.Checked)
            self._list.addItem(entry)
        self._list.itemChanged.connect(self._updateOk)
        button_layout = QVBoxLayout()
        all_button    = QPushButton("All")
        none_button   = QPushButton("None")
        invert_button = QPushButton("Invert")
        for button in (
            all_button, none_button, invert_button
        ):
            button.setAutoDefault(False)
            button_layout.addWidget(button)
        button_layout.addStretch()
        all_button.clicked.connect(self._onAll)
        none_button.clicked.connect(self._onNone)
        invert_button.clicked.connect(self._onInvert)
        layout.addWidget(self._list, 1)
        layout.addLayout(button_layout)
        self._updateOk()

    @checked
    def _updateOk(self : Self) -> None:
        if self._ok_button is None:
            return
        enabled = False
        for i in range(self._list.count()):
            item = self._list.item(i)
            if item is not None \
            and item.checkState() == Qt.CheckState.Checked:
                enabled = True
                break
        self._ok_button.setEnabled(enabled)

    @checked
    def _setAllChecked(self : Self, checked : bool) -> None:
        state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        self._list.blockSignals(True)
        for i in range(self._list.count()):
            item = self._list.item(i)
            if item is not None:
                item.setCheckState(state)
        self._list.blockSignals(False)
        self._updateOk()

    @checked
    def _onAll(self : Self) -> None:
        self._setAllChecked(True)

    @checked
    def _onNone(self : Self) -> None:
        self._setAllChecked(False)

    @checked
    def _onInvert(self : Self) -> None:
        self._list.blockSignals(True)
        for i in range(self._list.count()):
            item = self._list.item(i)
            if item is None:
                continue
            if item.checkState() == Qt.CheckState.Checked:
                item.setCheckState(Qt.CheckState.Unchecked)
            else:
                item.setCheckState(Qt.CheckState.Checked)
        self._list.blockSignals(False)
        self._updateOk()
