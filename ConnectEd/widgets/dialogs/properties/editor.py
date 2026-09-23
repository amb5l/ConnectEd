from __future__ import annotations

from typing import Self

from PyQt6.QtCore    import Qt, QItemSelection
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
    in a grid or bush.
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
        self._setMainWidget(self._grid_widget)
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
        self._view_combo.addItem("List", self._bush_widget)
        self._view_combo.currentIndexChanged.connect(self._onViewChanged)
        self._control_layout.addWidget(self._view_combo)
        # transpose label and checkbox
        self._transpose_label = QLabel("Transpose:")
        self._control_layout.addWidget(self._transpose_label)
        self._transpose_checkbox = QCheckBox()
        self._control_layout.addWidget(self._transpose_checkbox)
        # property buttons
        self._add_property_button = QPushButton("+ Property")
        self._add_property_button.setEnabled(False)
        self._add_property_button.clicked.connect(self._onAddProperty)
        self._control_layout.addWidget(self._add_property_button)
        self._del_property_button = QPushButton("- Property")
        self._del_property_button.setEnabled(False)
        self._del_property_button.clicked.connect(self._onDelProperty)
        self._control_layout.addWidget(self._del_property_button)
        # text buttons
        self._add_text_button = QPushButton("+ Text")
        self._add_text_button.setEnabled(False)
        self._add_text_button.clicked.connect(self._onAddText)
        self._control_layout.addWidget(self._add_text_button)
        self._del_text_button = QPushButton("- Text")
        self._del_text_button.setEnabled(False)
        self._del_text_button.clicked.connect(self._onDelText)
        self._control_layout.addWidget(self._del_text_button)
        # filter button
        self._filter_button = QPushButton("Filter")
        self._filter_button.setEnabled(False)
        self._filter_button.clicked.connect(self._onFilter)
        self._control_layout.addWidget(self._filter_button)
        # sort button
        self._sort_button = QPushButton("Sort")
        self._sort_button.setEnabled(False)
        self._sort_button.clicked.connect(self._onSort)
        self._control_layout.addWidget(self._sort_button)

    def onSelectionChanged(
        self       : Self,
        widget     : PropertiesGridWidget | PropertiesBushWidget,
        properties : int,
        texts      : int
    ) -> None:
        """Main widget has changed selection -> update button enables."""
        # filter unwanted calls
        if widget != self._main_widget:
            return
        # update button enables
        self._add_property_button .setEnabled(True)
        self._del_property_button .setEnabled(properties > 0)
        self._add_text_button     .setEnabled(properties == 1)
        self._del_text_button     .setEnabled(texts > 0)
        self._filter_button       .setEnabled(True)
        self._sort_button         .setEnabled(True)

    def _setMainWidget(
        self   : Self,
        widget : PropertiesGridWidget | PropertiesBushWidget
    ) -> None:
        # initialize
        if not hasattr(self, '_main_widget'):
            self._main_widget = widget
        # handle no-op
        elif self._main_widget == widget:
            return
        # update main widget
        else:
            self._main_widget = widget
            self._layout.replaceWidget(self._main_widget, widget)
        # clear selection
        self._main_widget.clearSelection()
        # update button enables
        self.selectionChanged(self._main_widget, QItemSelection(), QItemSelection())
        # update transpose checkbox
        if self._main_widget == self._grid_widget:
            # set transposed checkbox
            self._transpose_checkbox.setTristate(False)
            self._transpose_checkbox.setChecked(self._grid_widget.transposed())
            self._transpose_checkbox.setEnabled(True)
        elif self._main_widget == self._bush_widget:
            # disable transpose checkbox
            self._transpose_checkbox.setTristate(True)
            self._transpose_checkbox.setCheckState(
                Qt.CheckState.PartiallyChecked
            )
            self._transpose_checkbox.setEnabled(False)
        else:
            raise ValueError("Invalid main widget")

    def _onViewChanged(self, index: int) -> None:
        if self._view_combo is None:
            return
        current_data = self._view_combo.currentData()
        if isinstance(
            current_data, PropertiesBushWidget | PropertiesGridWidget
        ):
            self._setMainWidget(current_data)

    def _onAddProperty(self) -> None:
        pass  # TODO: implement

    def _onDelProperty(self) -> None:
        pass  # TODO: implement

    def _onAddText(self) -> None:
        pass  # TODO: implement

    def _onDelText(self) -> None:
        pass  # TODO: implement

    def _onFilter(self) -> None:
        pass  # TODO: implement

    def _onSort(self) -> None:
        pass  # TODO: implement


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
