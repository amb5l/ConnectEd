from __future__ import annotations

from typing import Self

from PyQt6.QtWidgets import QWidget, QComboBox, QCheckBox

from ...graphics.properties import Property, PropertiesMixin

from ..components.table import TableModel, TableView

from .list import PropertyFieldSpec, DisplayFieldSpec, _FIELD_SPECS


class SliceComboBox(QComboBox):
    """Slice (property attribute) picker."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        value_idx = 0
        for field in _FIELD_SPECS:
            if isinstance(field, PropertyFieldSpec) \
            or isinstance(field, DisplayFieldSpec):
                label = field.label
                if label == "Name" or label == "Custom":
                    continue
                self.addItem(label)
                if label == "Value":
                    value_idx = self.count() - 1
        self.setCurrentIndex(value_idx)


class PropertiesGridWidget(TableView):
    """
    Widget for displaying properties in a grid.
    """

    def __init__(
        self               : Self,
        items              : list[PropertiesMixin],
        transpose_checkbox : QCheckBox,
        parent             : QWidget | None = None
    ) -> None:
        if len(items) == 0:
            raise ValueError("Items list is empty")
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
