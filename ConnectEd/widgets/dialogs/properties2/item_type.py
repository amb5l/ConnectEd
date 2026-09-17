from __future__ import annotations

from typing import Self

from PyQt6.QtWidgets import QWidget, QTabWidget, \
                            QVBoxLayout, QHBoxLayout, \
                            QLabel, QComboBox, QCheckBox, QPushButton

from ...graphics.properties import PropertiesMixin

from ..components.table import TableModel

from .list import PropertiesListWidget
from .grid import PropertiesGridWidget


class PropertiesItemTypeWidget(QWidget):
    """
    Widget for displaying properties of a single item type in a list or grid.
    """

    _model              : TableModel
    _list_widget        : PropertiesListWidget
    _grid_widget        : PropertiesGridWidget | None
    _current_widget     : PropertiesListWidget | PropertiesGridWidget
    _control_layout     : QHBoxLayout
    _perspective_layout : QHBoxLayout | None
    _perspective_label  : QLabel | None
    _perspective_combo  : QComboBox | None
    _transpose_checkbox : QCheckBox
    _filter_button      : QPushButton
    _layout             : QVBoxLayout

    def __init__(
        self   : Self,
        items  : list[PropertiesMixin],
        parent : QWidget | None = None
    ) -> None:
        # superclass init
        super().__init__(parent)
        # create perspectives and control layout
        self._list_widget = PropertiesListWidget(
            items, self._transpose_checkbox
        )
        self._control_layout = QHBoxLayout()
        if len(items) > 1:
            self._perspective_layout = QHBoxLayout()
            self._perspective_label = QLabel("View:")
            self._perspective_layout.addWidget(self._perspective_label)
            self._perspective_combo = QComboBox()
            self._perspective_combo.addItem("List", self._list_widget)
            self._perspective_combo.addItem("Grid", self._grid_widget)
            self._perspective_combo.currentIndexChanged.connect(
                self._onPerspectiveChanged
            )
            self._perspective_layout.addWidget(self._perspective_combo)
            self._control_layout.addLayout(self._perspective_layout)
            self._grid_widget = PropertiesGridWidget(
                items, self._transpose_checkbox
            )
        else:
            self._perspective_layout = None
            self._perspective_label = None
            self._perspective_combo = None
            self._grid_widget = None
        self._transpose_checkbox = QCheckBox()
        self._control_layout.addWidget(self._transpose_checkbox)
        # build top layout
        self._layout = QVBoxLayout(self)
        self._layout.addWidget(self._list_widget)
        self._layout.addLayout(self._control_layout)
        self.setLayout(self._layout)

    def _onPerspectiveChanged(self, index: int) -> None:
        if self._perspective_combo is None:
            return
        current_data = self._perspective_combo.currentData()
        if isinstance(
            current_data, PropertiesListWidget | PropertiesGridWidget
        ):
            # update layout
            self._layout.replaceWidget(self._current_widget, current_data)
            self._current_widget = current_data


class PropertiesItemTypeTabWidget(QTabWidget):
    """
    Widget for displaying multiple PropertiesItemTypeWidget tabs.
    """
