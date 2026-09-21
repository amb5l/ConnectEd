from __future__ import annotations

from typing import Self

from PyQt6.QtWidgets import QWidget, QTabWidget, \
                            QVBoxLayout, QHBoxLayout, \
                            QLabel, QComboBox, QCheckBox, QPushButton

from ...table.model import TableModel

from .grid import PropertiesGridWidget
from .bush import PropertiesBushWidget

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import OwnerStore


class PropertiesItemTypeWidget(QWidget):
    """
    Widget for displaying properties of a single item type,
    in a bush or grid.
    """

    _model              : TableModel
    _grid_widget        : PropertiesGridWidget | None
    _bush_widget        : PropertiesBushWidget
    _current_widget     : PropertiesGridWidget | PropertiesBushWidget
    _control_layout     : QHBoxLayout
    _perspective_layout : QHBoxLayout | None
    _perspective_label  : QLabel | None
    _perspective_combo  : QComboBox | None
    _transpose_checkbox : QCheckBox
    _filter_button      : QPushButton
    _layout             : QVBoxLayout

    def __init__(
        self   : Self,
        store  : OwnerStore,
        parent : QWidget | None = None
    ) -> None:
        # superclass init
        super().__init__(parent)
        # create perspectives and control layout
        self._bush_widget = PropertiesBushWidget(
            items, self._transpose_checkbox
        )
        self._control_layout = QHBoxLayout()
        if len(items) > 1:
            self._perspective_layout = QHBoxLayout()
            self._perspective_label = QLabel("View:")
            self._perspective_layout.addWidget(self._perspective_label)
            self._perspective_combo = QComboBox()
            self._perspective_combo.addItem("Bush", self._bush_widget)
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
        self._layout.addWidget(self._bush_widget)
        self._layout.addLayout(self._control_layout)
        self.setLayout(self._layout)

    def _onPerspectiveChanged(self, index: int) -> None:
        if self._perspective_combo is None:
            return
        current_data = self._perspective_combo.currentData()
        if isinstance(
            current_data, PropertiesBushWidget | PropertiesGridWidget
        ):
            # update layout
            self._layout.replaceWidget(self._current_widget, current_data)
            self._current_widget = current_data


_TAB_ORDER = [
    "Diagrams",
    "Blocks",
    "Symbols",
    "Gates",
    "Ports",
    "Net Labels",
    "Taps",
    "Lines",
    "Rectangles",
    "Ellipses",
    "Polylines",
    "Bitmaps",
    "Property Texts"
]


class PropertiesItemTypeTabWidget(QTabWidget):
    """
    Widget for displaying multiple PropertiesItemTypeWidget tabs.
    """

    def __init__(
        self   : Self,
        store : dict[str, OwnerStore],
        parent : QWidget | None = None
    ) -> None:
        # superclass init
        super().__init__(parent)
        # sort owner types
        owner_type_names = \
            sorted(store.keys(), key=lambda x: _TAB_ORDER.index(x))
        # create tabs
        for owner_type_name in owner_type_names:
            tab = PropertiesItemTypeWidget(store[owner_type_name])
            self.addTab(tab, owner_type_name)
