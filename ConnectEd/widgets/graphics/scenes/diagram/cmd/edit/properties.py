from __future__ import annotations

from typing      import Self, Any
from dataclasses import dataclass

from PyQt6.QtGui  import QColor

from .......app import logger

from .......core.check import checked
from .......core.types import NoChange, NO_CHANGE, AlignH, AlignV, \
                                   DataKind, HandleId, RectHandleId

from .....properties import PropertiesMixin, \
                            PropertyDisplayState, PropertyDisplayChange

from .....items.property_text import PropertyTextItem

from .. import CmdBase


class CmdPropertyBase(CmdBase):
    """Base class for property commands."""

    _owner : PropertiesMixin

    @checked
    def __init__(
        self  : Self,
        owner : PropertiesMixin
    ) -> None:
        self._owner = owner


class CmdAddProperty(CmdPropertyBase):
    """Command to add a property."""

    _name  : str
    _kind  : DataKind
    _value : Any

    @checked
    def __init__(
        self  : Self,
        owner : PropertiesMixin,
        name  : str,
        kind  : DataKind,
        value : Any
    ) -> None:
        super().__init__(owner)
        if name in owner.properties:
            logger().error(f"Property '{name}' already exists")
            self.setObsolete(True)
            return
        self._name  = name
        self._kind  = kind
        self._value = value

    @checked
    def redo(self : Self) -> None:
        self._owner.propertyAdd(self._name, self._kind, self._value)

    @checked
    def undo(self : Self) -> None:
        self._owner.propertyDelete(self._name)


class CmdEditProperty(CmdPropertyBase):
    _old_name  : str
    _old_kind  : DataKind
    _old_value : Any
    _new_name  : str      | NoChange
    _new_kind  : DataKind | NoChange
    _new_value : Any      | NoChange

    @checked
    def __init__(
        self  : Self,
        owner : PropertiesMixin,
        name  : str | tuple[str, str],
        old_kind  : DataKind | NoChange = NO_CHANGE,
        old_value : Any      | NoChange = NO_CHANGE
    ) -> None:
        super().__init__(owner)
        old_name, new_name = \
            name if isinstance(name, tuple) else (name, NO_CHANGE)
        if old_name not in owner.properties:
            logger().error(f"Property '{old_name}' not found")
            self.setObsolete(True)
            return
        old_kind = owner.properties[old_name].kind()
        old_value = owner.properties[old_name].value(raw = True)
        self._old_name  = old_name
        self._old_kind  = old_kind
        self._old_value = old_value
        self._new_name  = NO_CHANGE if old_name == new_name else new_name
        self._new_kind  = NO_CHANGE if old_kind == old_kind else old_kind
        self._new_value = NO_CHANGE if old_value == old_value else old_value

    @checked
    def redo(self : Self) -> None:
        name = self._old_name
        if not isinstance(self._new_name, NoChange):
            self._owner.propertyRename(name, self._new_name)
            name = self._new_name
        if not isinstance(self._new_kind, NoChange):
            self._owner.properties[name].setKind(self._new_kind)
        if not isinstance(self._new_value, NoChange):
            self._owner.properties[name].setValue(self._new_value)

    @checked
    def undo(self : Self) -> None:
        if not isinstance(self._new_name, NoChange):
            self._owner.propertyRename(self._new_name, self._old_name)
        name = self._old_name
        if not isinstance(self._new_kind, NoChange):
            self._owner.properties[name].setKind(self._old_kind)
        if not isinstance(self._new_value, NoChange):
            self._owner.properties[name].setValue(self._old_value)


class CmdDelProperty(CmdPropertyBase):
    _name        : str
    _kind        : DataKind
    _value       : Any
    _cmd_display : CmdSetPropertyDisplay | None

    @checked
    def __init__(
        self  : Self,
        owner : PropertiesMixin,
        name  : str
    ) -> None:
        super().__init__(owner)
        if name not in owner.properties:
            logger().error(f"Property '{name}' not found")
            self.setObsolete(True)
            return
        self._name  = name
        property = owner.properties[name]
        if property.isInherent():
            logger().error(f"Property '{name}' is inherent")
            self.setObsolete(True)
            return
        self._kind  = property.kind()
        self._value = property.value(raw = True)
        self._cmd_display = None
        if property.displayItem() is not None:
            self._cmd_display = CmdSetPropertyDisplay(owner, name, False)

    @checked
    def redo(self : Self) -> None:
        if self._cmd_display is not None:
            self._cmd_display.redo()
        self._owner.propertyDelete(self._name)

    @checked
    def undo(self : Self) -> None:
        self._owner.propertyAdd(self._name, self._kind, self._value)
        if self._cmd_display is not None:
            self._cmd_display.undo()


class CmdSetPropertyDisplay(CmdPropertyBase):
    """Command for setting property display on or off."""

    _name   : str
    _state  : PropertyDisplayState | None
    _enable : bool

    def __init__(
        self   : Self,
        owner  : PropertiesMixin,
        name   : str,
        enable : bool
    ) -> None:
        super().__init__(owner)
        if name not in owner.properties:
            logger().error(f"Property '{name}' not found")
            self.setObsolete(True)
            return
        self._name = name
        property = owner.properties[name]
        display_item = property.displayItem()
        if enable == (display_item is not None):
            self.setObsolete(True)
            return
        self._state = None
        if not enable:
            if display_item is not None:
                self._state = display_item.state()
        self._enable = enable

    def redo(self : Self) -> None:
        property = self._owner.properties[self._name]
        property.setDisplay(self._enable)

    def undo(self : Self) -> None:
        property = self._owner.properties[self._name]
        property.setDisplay(not self._enable)
        if self._state is not None:
            display_item = property.displayItem()
            if display_item is not None:
                display_item.apply(self._state)


class CmdEditPropertyDisplay(CmdPropertyBase):
    """Command for editing property display appearance."""

    _item   : PropertyTextItem
    _before : PropertyDisplayState
    _change : PropertyDisplayChange

    def __init__(
        self   : Self,
        owner  : PropertiesMixin,
        name   : str,
        change : PropertyDisplayChange
    ) -> None:
        super().__init__(owner)
        if name not in owner.properties:
            logger().error(f"Property '{name}' not found")
            self.setObsolete(True)
            return
        if change.noop():
            self.setObsolete(True)
            return
        display_item = owner.properties[name].displayItem()
        if display_item is None:
            logger().error(f"Property '{name}' does not have a display item")
            self.setObsolete(True)
            return
        self._item = display_item
        self._before = display_item.state()
        self._change = change

    def redo(self : Self) -> None:
        self._item.apply(self._change)

    def undo(self : Self) -> None:
        self._item.apply(self._before)
