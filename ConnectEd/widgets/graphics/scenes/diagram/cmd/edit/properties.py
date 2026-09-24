from __future__ import annotations

from typing import Self

from .......app import logger

from .......core.check import checked
from .......core.types import NoChange, DataKind
from .......core.utils import camel2proper

from .....properties import PropertiesMixin, Property, PropertyState, \
                            PropertyChange

from .....items.property_text import PropertyTextItem, PropertyTextState, \
                                     PropertyTextChange

from .. import CmdBase


class CmdPropertyBase(CmdBase):
    """Base class for property commands."""

    _owner : PropertiesMixin

    @checked
    def __init__(
        self  : Self,
        owner : PropertiesMixin
    ) -> None:
        text = camel2proper(self.__class__.__name__.replace("Cmd", ""))
        super().__init__(text)
        self._owner = owner


class CmdAddProperty(CmdPropertyBase):
    """Command to add a property."""

    _state    : PropertyState
    _property : Property

    @checked
    def __init__(
        self  : Self,
        owner : PropertiesMixin,
        state : PropertyState
    ) -> None:
        super().__init__(owner)
        if state.name in owner.properties:
            logger().error(f"Property '{state.name}' already exists")
            self.setObsolete(True)
            return
        if state.kind not in (DataKind.STR, DataKind.TEXT):
            logger().error(f"Invalid property kind: {state.kind}")
            self.setObsolete(True)
            return
        self._state    = state
        self._property = Property(owner, state.kind, state.value)

    @checked
    def redo(self : Self) -> None:
        if self._state.name in self._owner.properties:
            logger().error(f"Property '{self._state.name}' already exists")
            return
        self._owner.properties[self._state.name] = self._property

    @checked
    def undo(self : Self) -> None:
        name = self._owner.propertyName(self._property)
        if name is None:
            logger().error(f"Property '{self._state.name}' not found")
            return
        self._owner.propertyDelete(name)

    def property(self : Self) -> Property:
        return self._property


class CmdEditProperty(CmdPropertyBase):
    """Command to edit a property."""

    _property : Property
    _before   : PropertyState
    _change   : PropertyChange

    @checked
    def __init__(
        self     : Self,
        owner    : PropertiesMixin,
        property : Property,
        change   : PropertyChange
    ) -> None:
        super().__init__(owner)
        if owner.propertyName(property) is None:
            logger().error("Property does not belong to owner")
            self.setObsolete(True)
            return
        if change.noop():
            self.setObsolete(True)
            return
        self._property = property
        self._before   = property.state()
        self._change   = change

    @checked
    def redo(self : Self) -> None:
        self._apply(self._change)

    @checked
    def undo(self : Self) -> None:
        self._apply(self._before)

    @checked
    def _apply(
        self    : Self,
        payload : PropertyState | PropertyChange
    ) -> None:
        name = self._owner.propertyName(self._property)
        if name is None:
            logger().error("Property does not belong to owner")
            return
        if not isinstance(payload.name, NoChange) and payload.name != name:
            self._owner.propertyRename(name, payload.name)
        if not isinstance(payload.kind, NoChange):
            self._property.setKind(payload.kind)
        if not isinstance(payload.value, NoChange):
            self._property.setValue(payload.value)


class CmdDelProperty(CmdPropertyBase):
    """Command to delete a property and its texts."""

    _name     : str
    _property : Property
    _texts    : list[CmdDelPropertyText]

    @checked
    def __init__(
        self     : Self,
        owner    : PropertiesMixin,
        property : Property
    ) -> None:
        super().__init__(owner)
        name = owner.propertyName(property)
        if name is None:
            logger().error("Property does not belong to owner")
            self.setObsolete(True)
            return
        if property.isInherent():
            logger().error(f"Property '{name}' is inherent")
            self.setObsolete(True)
            return
        self._name     = name
        self._property = property
        self._texts    = [
            CmdDelPropertyText(owner, text)
            for text in owner.propertyTextItems(property)
        ]

    @checked
    def redo(self : Self) -> None:
        for text in self._texts:
            text.redo()
        name = self._owner.propertyName(self._property)
        if name is None:
            logger().error(f"Property '{self._name}' not found")
            return
        self._owner.propertyDelete(name)

    @checked
    def undo(self : Self) -> None:
        if self._name in self._owner.properties:
            logger().error(f"Property '{self._name}' already exists")
            return
        self._owner.properties[self._name] = self._property
        for text in reversed(self._texts):
            text.undo()


class CmdAddPropertyText(CmdPropertyBase):
    """Command to add a property text."""

    _property : Property
    _state    : PropertyTextState
    _item     : PropertyTextItem | None

    @checked
    def __init__(
        self     : Self,
        owner    : PropertiesMixin,
        property : Property,
        state    : PropertyTextState
    ) -> None:
        super().__init__(owner)
        if owner.propertyName(property) is None:
            logger().error("Property does not belong to owner")
            self.setObsolete(True)
            return
        self._property = property
        self._state    = state
        self._item     = None

    @checked
    def redo(self : Self) -> None:
        if self._item is None:
            text = self._owner.propertyTextAdd(self._property)
            text.apply(self._state)
            self._item = text
            return
        self._owner.propertyTextAttach(self._item)

    @checked
    def undo(self : Self) -> None:
        if self._item is None:
            return
        self._owner.propertyTextRemove(self._item)


class CmdEditPropertyText(CmdPropertyBase):
    """Command to edit a property text."""

    _item   : PropertyTextItem
    _before : PropertyTextState
    _change : PropertyTextChange

    @checked
    def __init__(
        self   : Self,
        item   : PropertyTextItem,
        change : PropertyTextChange
    ) -> None:
        super().__init__(item.property().owner())
        if change.item is not item:
            logger().error("Property text change is for a different text")
            self.setObsolete(True)
            return
        if change.noop():
            self.setObsolete(True)
            return
        if not any(
            text is item
            for text in self._owner.propertyTextItems(item.property())
        ):
            logger().error("Property text is not on owner")
            self.setObsolete(True)
            return
        self._item   = item
        self._before = item.state()
        self._change = change

    @checked
    def redo(self : Self) -> None:
        self._item.apply(self._change)

    @checked
    def undo(self : Self) -> None:
        self._item.apply(self._before)


class CmdDelPropertyText(CmdPropertyBase):
    """Command to delete a property text."""

    _item : PropertyTextItem

    @checked
    def __init__(
        self  : Self,
        owner : PropertiesMixin,
        item  : PropertyTextItem
    ) -> None:
        super().__init__(owner)
        if item.property().owner() is not owner:
            logger().error("Property text does not belong to owner")
            self.setObsolete(True)
            return
        if not any(
            text is item
            for text in owner.propertyTextItems(item.property())
        ):
            logger().error("Property text is not on owner")
            self.setObsolete(True)
            return
        self._item = item

    @checked
    def redo(self : Self) -> None:
        self._owner.propertyTextRemove(self._item)

    @checked
    def undo(self : Self) -> None:
        self._owner.propertyTextAttach(self._item)
