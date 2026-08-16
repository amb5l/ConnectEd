from __future__ import annotations

import re

from typing          import Self, Any, Literal, TypeVar, Generic, TypeAlias
from collections.abc import Callable
from dataclasses     import dataclass

from PyQt6.QtCore import QObject, pyqtSignal

from ..app import logger

from .check import checked
from .types import DataKind
from .utils import val2str, str2val


class PropertyNotifier(QObject):
    changed = pyqtSignal()


T = TypeVar("T")


@dataclass
class InherentProperty(Generic[T]):
    kind     : DataKind | Callable[[T], DataKind]  | None = None
    worthy   : Literal[True] | Callable[[T], bool] | None = True
    getter   : Callable[[T], Any]                  | None = None
    setter   : Callable[[T, Any], None]            | None = None
    default  : Callable[[T], Any]                  | None = None
    notifier : PropertyNotifier                    | None = None
    tip      : str                                 | None = None


CustomPropertyType : TypeAlias = str | int | float | bool

_CUSTOM_PROPERTY_KINDS = (
    DataKind.STR, DataKind.TEXT, DataKind.INT, DataKind.FLOAT, DataKind.BOOL
)


@dataclass
class CustomProperty:
    kind     : DataKind
    value    : CustomPropertyType | None = None
    notifier : PropertyNotifier   | None = None


PropertiesDict : TypeAlias = \
    dict[str, InherentProperty[Any] | CustomProperty]


class PropertiesMixin:
    _PROPERTIES : PropertiesDict
    _properties : PropertiesDict

    def initProperties(self : Self, live : bool) -> None:
        self._properties = {}
        self._live = live

    def propertiesLive(self : Self) -> bool:
        return self._live

    @checked
    def setPropertiesLive(self : Self, live : bool) -> None:
        self._live = live

    @checked
    def propertyNames(self : Self) -> list[str]:
        return list(self._properties.keys())

    @checked
    def propertyInherentNames(self : Self) -> list[str]:
        return [
            name for name, property in self._properties.items()
            if isinstance(property, InherentProperty)
        ]

    @checked
    def propertyCustomNames(self : Self) -> list[str]:
        return [
            name for name, property in self._properties.items()
            if isinstance(property, CustomProperty)
        ]

    @checked
    def propertyExists(self : Self, name : str) -> bool:
        """
        Test property existance.
        Returns True if the property exists, False otherwise.
        """
        return name in self._properties

    @checked
    def propertyInherent(self : Self, name : str) -> bool | None:
        """
        Test if a property is inherent.
        Returns True if the property is inherent, False otherwise.
        """
        # check property existence
        if not self.propertyExists(name):
            logger().warning(f"Property '{name}' not found")
            return None
        # get property instance
        property = self._properties[name]
        # test if inherent
        return isinstance(property, InherentProperty)

    @checked
    def propertyWriteable(self : Self, name : str) -> bool | None:
        """
        Test if a property is writeable.
        Returns True if the property is writeable, False otherwise.
        """
        # check property existence
        if not self.propertyExists(name):
            logger().warning(f"Property '{name}' not found")
            return None
        # get property instance
        property = self._properties[name]
        # test if writeable
        return isinstance(property, CustomProperty) or callable(property.setter)

    @checked
    def propertyKind(self : Self, name : str) -> DataKind | None:
        # check property existence
        if not self.propertyExists(name):
            logger().warning(f"Property '{name}' not found")
            return None
        # get property instance
        property = self._properties[name]
        # return kind
        if callable(property.kind):
            try:
                return property.kind(self)
            except Exception:
                return None
        return property.kind

    @checked
    def setPropertyKind(self : Self, name : str, kind : DataKind) -> bool:
        """
        Set the kind of a property - allowed for custom properties only.
        Returns True if the property was set, False otherwise.
        """
        # check property existence
        if not self.propertyExists(name):
            logger().warning(f"Property '{name}' not found")
            return False
        property = self._properties[name]
        # check property is custom
        if not isinstance(property, CustomProperty):
            logger().warning(f"Property '{name}' is not custom")
            return False
        # set kind
        property.kind = kind
        self.propertySignalChanges(name)
        return True

    @checked
    def propertyWorthy(self : Self, name : str) -> bool:
        """
        Test if a property is worthy of serialization.
        Returns True if the property is worthy, False otherwise.
        """
        # check property existence
        if not self.propertyExists(name):
            logger().warning(f"Property '{name}' not found")
            return False
        # get validity
        if isinstance(property := self._properties[name], InherentProperty):
            return property.worthy is True or \
                (callable(property.worthy) and property.worthy(self))
        elif isinstance(property, CustomProperty):
            return True
        else:
            logger().warning(f"Bad property type: {type(property)}")
            return False

    @checked
    def propertyDefaultValue(self : Self, name : str) -> Any:
        """
        Get the default value of a property.
        Returns the default value of the property if found, None otherwise.
        """
        # check property existence
        if not self.propertyExists(name):
            logger().warning(f"Property '{name}' not found")
            return None
        # get property instance
        property = self._properties[name]
        # get default value
        if isinstance(property, InherentProperty) and callable(property.default):
            return property.default(self)
        # not found
        return None

    @checked
    def propertyValue(
        self   : Self,
        name   : str,
        slot   : Callable  | None = None,  # e.g. PropertyTextItem.onTextChanged
        trail  : list[str] | None = None   # substitution recursion trail
    ) -> Any:
        """
        Get the value of a property. Supports substitution of other properties;
        for items these can be scene properties.
        If a slot is provided, ensures that a property notifier exists and is
        connected to it.
        Returns the value of the property if found, otherwise None.
        """
        # check property existence
        if not self.propertyExists(name):
            logger().warning(f"Property '{name}' not found: {trail}")
            return None
        # detect recursion issues
        if trail is not None:  # substitution in progress
            if name in trail:
                logger().warning(
                    f"Property '{name}' substitution recursion loop detected: {trail}"
                )
                return None
            trail = trail + [name]
            if len(trail) > 10:
                logger().warning(
                    f"Property substitution recursion depth exceeded: {trail}"
                )
                return None
        # get property instance
        property = self._properties[name]
        # if slot is specified, connect the notifier to it
        if slot:
            # ensure that a notifier exists
            property.notifier = property.notifier or PropertyNotifier()
            # avoid duplicate connections
            try:
                property.notifier.changed.disconnect(slot)
            except TypeError:
                pass
            property.notifier.changed.connect(slot)
        # inherent properties
        if isinstance(property, InherentProperty):
            if not callable(property.getter):
                logger().warning(f"Property '{name}' has no getter: {trail}")
                return None
            else:
                return property.getter(self)
        # custom properties
        elif isinstance(property, CustomProperty):
            kind = property.kind
            if kind != DataKind.STR and kind != DataKind.TEXT:  # not a string
                return property.value
             # substitution
            def repl(match: re.Match) -> str:
                var_name = match.group(1)
                # look locally, then (for items) in the scene
                if self.propertyExists(var_name):
                    return str(self.propertyValue(var_name, slot, trail))
                else:
                    properties_parent = self.propertiesParent()
                    if properties_parent is not None \
                    and properties_parent.propertyExists(var_name):
                            return str(
                                properties_parent.propertyValue(var_name, slot, trail)
                            )
                return f"<{var_name}>"  # unresolved substitution
            return re.sub(r'\{(\w+)\}', repl, val2str(property.value))
        # unknown properties
        logger().warning(f"Property '{name}' has unknown type: {type(property)}")
        return None

    @checked
    def setPropertyValue(self : Self, name : str, value : Any) -> bool:
        """
        Set the value of a property.
        Returns True if the property was set, False otherwise.
        """
        # check property existence
        if not self.propertyExists(name):
            logger().warning(f"Property '{name}' not found")
            return False
        property = self._properties[name]
        # get kind
        if not isinstance(kind := self.propertyKind(name), DataKind):
            raise TypeError("Bad kind")
        # inherent properties
        if isinstance(property, InherentProperty):
            if not callable(property.setter):
                logger().warning(f"Property '{name}' is read-only")
                return False
            # convert from str to appropriate type if necessary
            if isinstance(value, str) and kind != DataKind.STR:
                value = str2val(value, kind.types()[0].__name__)
            property.setter(self, value)
            return True
        # custom properties
        elif isinstance(property, CustomProperty):
            if isinstance(value, kind.types()):
                property.value = value
            else:
                logger().warning(f"Bad property value type: {type(value)}")
                return False
            self.propertySignalChanges(name)
            return True
        # unknown properties
        logger().warning(f"Bad property type: {type(property)}")
        return False

    @checked
    def propertyInit(self : Self, name : str, value : Any) -> bool:
        """
        Initialize a property. Creates if required, and sets the value;
        for use in deserialization, and for creating new custom properties.
        Returns True if the property was initialized, False otherwise.
        """
        if self.propertyExists(name):
            return self.setPropertyValue(name, value)
        if isinstance(value, bool):
            kind = DataKind.BOOL
        elif isinstance(value, int):
            kind = DataKind.INT
        elif isinstance(value, float):
            kind = DataKind.FLOAT
        else:
            kind = DataKind.STR
        return self.propertyAdd(name, kind, value)

    @checked
    def propertyAdd(
        self  : Self,
        name  : str,
        kind  : DataKind,
        value : Any
    ) -> bool:
        """
        Add a property.
        Returns True if the property was added, False otherwise.
        """
        # check for existing property
        if self.propertyExists(name):
            logger().warning(f"Property '{name}' already exists")
            return False
        # check kind
        if kind not in _CUSTOM_PROPERTY_KINDS:
            logger().warning(f"Invalid property kind: {kind}")
            return False
        # create custom property
        self._properties[name] = CustomProperty(kind=kind, value=value)
        return True

    @checked
    def propertyRename(self : Self, old_name : str, new_name : str) -> bool:
        """
        Rename a property.
        Returns True if the property was renamed, False otherwise.
        """
        # check for existing property
        if not self.propertyExists(old_name):
            logger().warning(f"Property '{old_name}' not found")
            return False
        # check for no change
        if old_name == new_name:
            logger().info(f"Old and new names are the same: {old_name}")
            return False
        # check for clash with existing property
        if self.propertyExists(new_name):
            logger().warning(f"Property '{new_name}' already exists")
            return False
        # get property instance
        property = self._properties[old_name]
        # check if inherent
        if isinstance(property, InherentProperty):
            logger().warning(f"Cannot rename inherent property '{old_name}'")
            return False
        # rename
        self._properties[new_name] = property
        del self._properties[old_name]
        # notify subscribers
        self.propertySignalChanges(new_name)
        # rename substitutions
        pattern = r'(?<!\\)\{' + re.escape(old_name) + r'\}'
        repl = '{' + new_name + '}'
        subst_changed : list[str] = []
        for name, prop in self._properties.items():
            if name == new_name or not isinstance(prop, CustomProperty):
                continue
            if prop.kind not in (DataKind.STR, DataKind.TEXT):
                continue
            if not isinstance(prop.value, str):
                logger().warning(f"Property '{name}' has non-string value")
                continue
            if old_name in prop.value:
                new_value = re.sub(pattern, repl, prop.value)
                prop.value = new_value
                subst_changed.append(name)
        # notify substitution subscribers
        if subst_changed:
            self.propertySignalChanges(subst_changed)
        # done
        return True

    @checked
    def propertyDelete(self : Self, name : str) -> bool:
        """
        Remove a property (and its associated property text item if applicable).
        Returns True if the property was removed, False otherwise.
        """
        # check property existence
        if not self.propertyExists(name):
            logger().warning(f"Property '{name}' not found")
            return False
        # get property instance
        property = self._properties[name]
        # check if inherent
        if isinstance(property, InherentProperty):
            logger().warning(f"Inherent property '{name}' cannot be removed")
            return False
        # notify property receivers
        self.propertySignalChanges(name)
        # remove property from dictionary
        del self._properties[name]
        # done
        return True

    @checked
    def propertySignalChanges(self : Self, names : str | list[str]) -> None:
        if not self.propertiesLive():
            return
        if isinstance(names, str):
            names = [names]
        for name in names:
            if self.propertyExists(name):
                property = self._properties[name]
                if property.notifier:
                    property.notifier.changed.emit()

    @checked
    def propertySubscribe(self : Self, name : str, slot : Callable) -> None:
        if not self.propertyExists(name):
            logger().error(f"Property '{name}' not found")
            return
        property = self._properties[name]
        if property.notifier is None:
            logger().error(f"Property '{name}' has no notifier")
            return
        property.notifier.changed.connect(slot)

    @checked
    def propertyUnsubscribe(self : Self, name : str, slot : Callable) -> None:
        if not self.propertyExists(name):
            logger().error(f"Property '{name}' not found")
            return
        property = self._properties[name]
        if property.notifier is None:
            logger().error(f"Property '{name}' has no notifier")
            return
        property.notifier.changed.disconnect(slot)

    @checked
    def propertySyncInherentFrom(self  : Self, other : PropertiesMixin) -> None:
        for name in other.propertyInherentNames():
            if self.propertyExists(name):
                if self.propertyWriteable(name):
                    self.setPropertyValue(name, other.propertyValue(name))
            else:
                logger().warning(f"Property '{name}' not found")

    @checked
    def propertySyncCustomFrom(self : Self, other : PropertiesMixin) -> None:
        for name in self.propertyCustomNames():
            if not other.propertyExists(name):
                self.propertyDelete(name)
            else:
                self.setPropertyValue(name, other.propertyValue(name))
        for name in other.propertyCustomNames():
            if self.propertyExists(name):
                self.setPropertyValue(name, other.propertyValue(name))
            else:
                kind = other.propertyKind(name)
                if not isinstance(kind, DataKind):
                    raise TypeError("Bad kind")
                self.propertyAdd(name, kind, other.propertyValue(name))

    def propertiesParent(self : Self) -> PropertiesMixin | None:
        """Override to return the properties parent e.g. scene for item."""
        return None
