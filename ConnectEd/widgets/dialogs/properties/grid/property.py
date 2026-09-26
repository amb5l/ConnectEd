from __future__ import annotations

from typing import Self, Any

from PyQt6.QtWidgets import QDialog, QWidget, \
                            QVBoxLayout, QHBoxLayout, \
                            QLabel, QLineEdit

from .....core.check                import checked
from .....core.types                import NoChange, DataKind

from ....utils                      import kind2dialogEditor

from ....graphics.properties        import (
    Property, PropertyPending, PropertyAndTextsEdit, PropertiesMixin
)

from ...components.combo.enum       import EnumComboBox
from ...components.layout.ok_cancel import OkCancelLayout

from .text_table                    import PropertyTextTableWidget


class PropertyDialog(QDialog):
    """
    Dialog for editing a property and its texts.
    Normally opened from PropertiesGridWidget.
    Text editing launches another dialog.
    """

    _pending       : PropertyPending
    _owner         : PropertiesMixin

    _layout        : QVBoxLayout
    _name_layout   : QHBoxLayout
    _name_label    : QLabel
    _name_edit     : QLineEdit
    _nature_layout : QHBoxLayout
    _nature_label  : QLabel
    _nature_value  : QLabel
    _kind_layout   : QHBoxLayout
    _kind_label    : QLabel
    _kind_value    : EnumComboBox
    _value_layout  : QHBoxLayout
    _value_label   : QLabel
    _value_value   : QWidget  # various widgets for various kinds
    _texts_label   : QLabel
    _texts_widget  : PropertyTextTableWidget  # texts table

    @checked
    def __init__(
        self   : Self,
        source : Property         | PropertyPending,
        parent : QWidget          | None = None,
        owner  : PropertiesMixin  | None = None,
    ) -> None:
        super().__init__(parent)
        if isinstance(source, Property):
            self._pending = PropertyPending(source)
            self._owner   = source.owner()
        else:
            self._pending = source
            if owner is not None:
                self._owner = owner
            elif source.obj is not None:
                self._owner = source.obj.owner()
            else:
                raise ValueError("Property pending has no owner")
        self._initUI()

    @checked
    def getEdits(self : Self) -> PropertyAndTextsEdit | None:
        """Copy the widgets into the pending and return its edits."""
        self._sync()
        return self._pending.getEdit(self._owner)

    def _initUI(self : Self) -> None:
        if self._pending.state is None:
            raise ValueError("Property pending state is None")
        self.setWindowTitle(self._pending.state.name)
        custom = self._pending.obj is None or self._pending.obj.isCustom()
        # name
        self._name_label = QLabel("Name:")
        self._name_edit = QLineEdit(self._pending.state.name)
        self._name_edit.setReadOnly(not custom)
        self._name_layout = QHBoxLayout()
        self._name_layout.addWidget(self._name_label)
        self._name_layout.addWidget(self._name_edit)
        # nature
        self._nature_label = QLabel("Nature:")
        self._nature_value = QLabel("Custom" if custom else "Inherent")
        self._nature_layout = QHBoxLayout()
        self._nature_layout.addWidget(self._nature_label)
        self._nature_layout.addWidget(self._nature_value)
        # kind
        self._kind_label = QLabel("Kind:")
        if custom:
            self._kind_value = EnumComboBox[DataKind](
                self._pending.state.kind, (DataKind.STR, DataKind.TEXT)
            )
        else:
            self._kind_value = EnumComboBox[DataKind](
                self._pending.state.kind, (self._pending.state.kind,)
            )
            self._kind_value.setEnabled(False)
        self._kind_value.currentIndexChanged.connect(self._onKindChanged)
        self._kind_layout = QHBoxLayout()
        self._kind_layout.addWidget(self._kind_label)
        self._kind_layout.addWidget(self._kind_value)
        # value
        self._value_label = QLabel("Value:")
        self._value_layout = QHBoxLayout()
        self._value_layout.addWidget(self._value_label)
        self._installValueEditor(
            self._pending.state.kind, self._pending.state.value
        )
        # text table
        self._texts_label = QLabel("Texts:")
        self._texts_widget = PropertyTextTableWidget(self._pending.texts)
        # put it all together
        self._layout = QVBoxLayout(self)
        self._layout.addLayout(self._name_layout)
        self._layout.addLayout(self._nature_layout)
        self._layout.addLayout(self._kind_layout)
        self._layout.addLayout(self._value_layout)
        self._layout.addWidget(self._texts_label)
        self._layout.addWidget(self._texts_widget, 1)
        self._layout.addLayout(OkCancelLayout(self))

    def _installValueEditor(self : Self, kind : DataKind, value : Any) -> None:
        widget = kind2dialogEditor(kind)(value=value)
        if self._pending.obj is not None and not self._pending.obj.writeable():
            widget.setEnabled(False)
        if hasattr(self, "_value_value"):
            self._value_layout.replaceWidget(self._value_value, widget)
            self._value_value.deleteLater()
        else:
            self._value_layout.addWidget(widget)
        self._value_value = widget

    def _onKindChanged(self : Self) -> None:
        state = self._pending.state
        if state is None:
            return
        kind = self._kind_value.raw()
        if not isinstance(kind, DataKind) or kind is state.kind:
            return
        self._syncValue()
        state.kind = kind
        self._installValueEditor(kind, state.value)

    def _sync(self : Self) -> None:
        state = self._pending.state
        if state is None:
            return
        if not self._name_edit.isReadOnly():
            state.name = self._name_edit.text()
        kind = self._kind_value.value()
        if not isinstance(kind, NoChange):
            state.kind = kind
        self._syncValue()

    def _syncValue(self : Self) -> None:
        state = self._pending.state
        if state is None or not hasattr(self, "_value_value"):
            return
        value = getattr(self._value_value, "value")()
        if not isinstance(value, NoChange):
            state.value = value
