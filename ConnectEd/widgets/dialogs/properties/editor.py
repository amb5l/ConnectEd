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


class PropertiesEditorWidget(QWidget):
    """
    Widget for displaying properties of a single item type,
    in a bush or grid.
    Control layout
    """

    _model               : TableModel

    _layout              : QVBoxLayout
    _grid_widget         : PropertiesGridWidget
    _bush_widget         : PropertiesBushWidget
    _main_widget         : PropertiesGridWidget | PropertiesBushWidget

    _control_layout      : QHBoxLayout
    _view_label          : QLabel
    _view_combo          : QComboBox
    _transpose_label     : QLabel
    _transpose_checkbox  : QCheckBox
    _add_property_button : QPushButton
    _del_property_button : QPushButton
    _add_text_button     : QPushButton
    _del_text_button     : QPushButton
    _filter_button       : QPushButton
    _sort_button         : QPushButton

    def __init__(
        self   : Self,
        store  : OwnerStore,
        parent : QWidget | None = None
    ) -> None:
        # superclass init
        super().__init__(parent)
        # control layout
        self._buildControlLayout()
        # grid widget
        self._grid_widget = PropertiesGridWidget(store, self._transpose_checkbox)
        # bush widget
        self._bush_widget = PropertiesBushWidget(store)
        # default main widget
        self._main_widget = self._grid_widget
        # dialog layout
        self._layout = QVBoxLayout(self)
        self._layout.addWidget(self._main_widget)
        self._layout.addLayout(self._control_layout)
        self.setLayout(self._layout)

    def _buildControlLayout(self) -> None:
        self._control_layout = QHBoxLayout()
        # view label and combo
        self._view_label = QLabel("View:")
        self._control_layout.addWidget(self._view_label)
        self._view_combo = QComboBox()
        self._view_combo.addItem("Grid", self._grid_widget)
        self._view_combo.addItem("Tree", self._bush_widget)
        self._view_combo.currentIndexChanged.connect(self._onViewChanged)
        self._control_layout.addWidget(self._view_combo)
        # transpose label and checkbox
        self._transpose_label = QLabel("Transpose:")
        self._control_layout.addWidget(self._transpose_label)
        self._transpose_checkbox = QCheckBox()
        self._control_layout.addWidget(self._transpose_checkbox)

    def _setMainWidget(
        self   : Self,
        widget : PropertiesGridWidget | PropertiesBushWidget
    ) -> None:
        self._main_widget = widget
        if self._main_widget == self._grid_widget:
            # set transposed checkbox

    def _onViewChanged(self, index: int) -> None:
        if self._view_combo is None:
            return
        current_data = self._view_combo.currentData()
        if isinstance(
            current_data, PropertiesBushWidget | PropertiesGridWidget
        ):
            # update layout
            self._layout.replaceWidget(self._main_widget, current_data)
            self._main_widget = current_data


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


class PropertiesEditorTabWidget(QTabWidget):
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
            tab = PropertiesEditorWidget(store[owner_type_name])
            self.addTab(tab, owner_type_name)
