from __future__ import annotations

from typing import Self

from PyQt6.QtCore    import QItemSelection
from PyQt6.QtGui     import QShowEvent
from PyQt6.QtWidgets import QWidget, QCheckBox, QHeaderView

from ....graphics.items.mixin import ItemMixin

from ....table.row   import TableRow
from ....table.model import TableModel, TableProxy
from ....table.view  import TableView

from ..item import PropertiesItem, PropertiesValueItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import OwnerStore
    from ....graphics.properties import PropertiesMixin


class PropertiesGridWidget(TableView):
    """
    One row per owner. The Item group holds the owner id. The Properties
    group holds one column per property name, showing that owner's value.
    Transpose turns owners into columns and properties into rows.
    """

    _store              : OwnerStore
    _model              : TableModel
    _proxy              : TableProxy
    _transpose_checkbox : QCheckBox
    _transposed         : bool

    def __init__(
        self               : Self,
        store              : OwnerStore,
        transpose_checkbox : QCheckBox,
        parent             : QWidget | None = None
    ) -> None:
        self._store = store
        self._transpose_checkbox = transpose_checkbox
        self._transposed = False
        self._model = TableModel()
        self._proxy = TableProxy()
        super().__init__(self._model, parent)
        self._proxy.setParent(self)
        self._proxy.setSourceModel(self._model)
        if (header := self.verticalHeader()) is not None:
            header.setSectionResizeMode(
                QHeaderView.ResizeMode.ResizeToContents
            )
            header.setVisible(False)
        transpose_checkbox.clicked.connect(self.onTransposedChanged)

    def showEvent(self, a0 : QShowEvent | None) -> None:
        """
        Rebuild from the store when shown, because another widget may have
        changed it.
        """
        super().showEvent(a0)
        self._rebuildModel()

    def selectionChanged(
        self       : Self,
        selected   : QItemSelection,
        deselected : QItemSelection
    ) -> None:
        from ..editor import PropertiesEditorWidget
        super().selectionChanged(selected, deselected)
        editor_widget = self.parent()
        if not isinstance(editor_widget, PropertiesEditorWidget):
            return
        # TODO: count selected properties and texts
        editor_widget.onSelectionChanged(self, 0, 0)

    def onTransposedChanged(self : Self, transposed : bool) -> None:
        self.setTransposed(transposed)

    def transposed(self) -> bool:
        return self._transposed

    def setTransposed(self, transposed : bool) -> None:
        if self._transpose_checkbox.isChecked() != transposed:
            self._transpose_checkbox.setChecked(transposed)
        if transposed == self._transposed:
            return
        self._transposed = transposed
        self._applyTranspose()

    def _applyTranspose(self : Self) -> None:
        """Show the source model, or the proxy that swaps rows and columns."""
        transposed = self._transposed
        self.setModel(self._proxy if transposed else self._model)
        # The id column becomes row 0. Its values are the column titles.
        model = self.model()
        if not isinstance(model, TableModel | TableProxy):
            raise ValueError("Bad model")
        if model.rowCount() > 0:
            self.setRowHidden(0, transposed)
        if (header := self.verticalHeader()) is not None:
            header.setVisible(transposed)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def _rebuildModel(self : Self) -> None:
        model = self._model
        model.clear()
        property_names = self._propertyNames()
        model.setHorizontalHeaderGroupLabels([
            ("Item", "ID"),
            *[("Properties", name) for name in property_names]
        ])
        owner_ids : list[str] = []
        for owner, drafts in self._store.items():
            by_name = {
                draft.state.name : draft
                for draft in drafts
                if draft.state is not None
            }
            row = TableRow(property_names)
            for name in property_names:
                draft = by_name.get(name)
                if draft is None or draft.state is None:
                    row[name] = PropertiesItem(
                        None, None, None, False, False, False
                    )
                    continue
                state = draft.state
                editable = draft.obj is None or draft.obj.writeable()
                row[name] = PropertiesValueItem(
                    state.kind, state.value, state, "value", False, editable
                )
            owner_id = self._ownerId(owner)
            model.appendRow([
                PropertiesItem(owner_id, owner, None, False, False),
                *row.cells()
            ])
            owner_ids.append(owner_id)
        model.setVerticalHeaderLabels(owner_ids)
        self._applyTranspose()

    def _propertyNames(self : Self) -> list[str]:
        names : list[str] = []
        for drafts in self._store.values():
            for draft in drafts:
                if draft.state is None or draft.state.name in names:
                    continue
                names.append(draft.state.name)
        return names

    def _ownerId(self : Self, owner : PropertiesMixin) -> str:
        if isinstance(owner, ItemMixin):
            return owner.suid()
        name = getattr(owner, "name", None)
        if callable(name):
            value = name()
            if isinstance(value, str) and value:
                return value
        return owner.description()
