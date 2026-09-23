from __future__ import annotations

from typing import Self

from PyQt6.QtCore    import QItemSelection
from PyQt6.QtWidgets import QWidget, QComboBox, QCheckBox


from ...table.model import TableModel
from ...table.view  import TableView

from .defs   import PropertyFieldSpec, DisplayFieldSpec, _FIELD_SPECS

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import OwnerStore
    from .editor import PropertiesEditorWidget


class PropertiesGridWidget(TableView):
    """
    Widget for displaying property values in a grid.
    User can dive into a property and access its texts by
    """

    _transposed : bool = False

    def __init__(
        self               : Self,
        store              : OwnerStore,
        transpose_checkbox : QCheckBox,
        parent             : QWidget | None = None
    ) -> None:
        # create model
        model = TableModel()
        # get property names
        property_names = set()
        for item in items:
            for property_name in item.properties.keys():
                property_names.add(property_name)
        # create header labels
        header_labels = ["Item ID"]
        for property_name in property_names:
            header_labels.append(property_name)
        model.setHorizontalHeaderLabels(header_labels)
        # create and add rows to model
        for item in items:
            row = []
            for property_name in property_names:
                property = item.properties[property_name]
                kind = property.kind
                value = property.value
                # table_item =
                row.append(table_item)
            model.appendRow(row)


        # create proxy

        # superclass init
        super().__init__(model, parent)

    def selectionChanged(
        self       : Self,
        selected   : QItemSelection,
        deselected : QItemSelection
    ) -> None:
        pass  # TODO: implement
        # call parent widget's selectionChanged method
        editor_widget = self.parent()
        if not isinstance(editor_widget, PropertiesEditorWidget):
            return
        self.parent().onSelectionChanged(selected, deselected)

    def transposed(self) -> bool:
        return self._transposed

    def setTransposed(self, transposed: bool) -> None:
        self._transposed = transposed
        # sort out header labels
