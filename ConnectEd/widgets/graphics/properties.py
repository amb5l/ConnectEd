"""
Properties System
=================

The properties system provides access to important attributes of items and
scenes, to facilitate...
- serialization and deserialization (to/from XML);
- tabular editing (dialogs and spreadsheets);
- embedding custom values.

Property values may be displayed by PropertyTextItem instances. Property value
changes are propagated to PropertyTextItem instances by signals.

Scene and item classes have /inherent/ properties; these may not be renamed or
deleted, and may be of any supported type e.g. float, QColor, etc. For example,
most item classes will have "X" and "Y" (position) properties.

Scene and item instances may also have /custom/ properties; these are always of
type Text (a string with a line/block format selection bool).

Custom properties may include the values of other properties, via substitution,
by enclosing the property name in curly braces. For example, "{Path}". The
substition mechanism searches the property owner's own properties, then (if the
owner is an item) the scene's properties.

Properties may optionally be excluded from serialization. For example, when a
property is empty, or has a default value. Properties may also be excluded from
tabular editing - this is typically used to create a "virtual" property that
exists only for use via substitution in custom properties. For example,
"ConnectEdVersion". Virtual properties will normally be provided by the scene.
"""

from typing          import Self, Any, Literal
from dataclasses     import dataclass
from collections.abc import Callable

import re

from PyQt6.QtCore import QPointF, QObject, pyqtSignal

from ...app import logger

from ...core import Text

from .items.property_text import PropertyTextItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .property import PropertySpec
    from .scenes.drawing import DrawingScene
    from .items import ItemType
    from .items.property_text import PropertyTextItem
    Owner = ItemType | DrawingScene


@dataclass
class PropertyTextSpec:
    anchor  : str
    pos     : QPointF | None = None
    origin  : str     | None = None
    block   : bool           = False


@dataclass
class PropertySpec:
    type_name : str                                              = "str"
    valid     : Literal[True] | Callable[["Owner"], bool] | None = True
    getter    : Callable[["Owner"], Any]                  | None = None
    setter    : Callable[["Owner", Any], None]            | None = None
    default   : Callable[["Owner"], Any]                  | None = None
    display   : PropertyTextSpec                          | None = None


class PropertySignaller(QObject):
    changed = pyqtSignal()


class PropertiesMixin:
    # class attributes
    _PROPERTY_SPECS : dict[str, "PropertySpec"]

    # instance attributes
    _custom_properties   : dict[str, Text]
    _property_signallers : dict[str, PropertySignaller]

    def initProperties(self : Self, bare : bool = False) -> None:
        """
        Initialize the properties system for this instance.
        """
        from .items.property_text import PropertyTextItem
        self._custom_properties   = {}
        self._property_signallers = {}
        if bare:
            return
        for name, spec in self._PROPERTY_SPECS.items():
            if not bare and spec.text is not None:
                property_text = PropertyTextItem(
                    name   = name,
                    cleat  = spec.text.anchor,
                    pos    = spec.text.pos,
                    origin = spec.text.origin,
                    parent = self.getHandle(spec.text.anchor)
                )
                property_text.onTextChange()

    def hasProperty(self : Self, name : str) -> bool:
        """
        Test if a property exists in this instance.
        Returns True if the property exists, False otherwise.
        """
        return name in self._PROPERTY_SPECS or name in self._custom_properties

    def getPropertyValue(
        self  : Self,
        name  : str,
        trail : list[str] | None = None  # substitution recursion trail
    ) -> Any | None:
        """
        Get the value of a property. Supports substitution of other properties.
        Returns the value of the property if found, otherwise None.
        """
        trail = trail or []
        if len(trail) > 10:
            name = trail[0]
            logger().warning(f"Property '{name}' substitution recursion depth exceeded")
            return None
        if name in self._PROPERTY_SPECS:
            spec = self._PROPERTY_SPECS[name]
            if spec.getter and callable(spec.getter):
                return spec._getter(self)  # callable
            else:
                logger().warning(f"Property '{name}' has no getter")
                return None
        elif name in self._custom_properties:
            raw = self._custom_properties[name]
            # substitute
            def repl(match: re.Match) -> str:
                var_name = match.group(1)
                return self.getPropertyValue(var_name, trail + [name])
            return re.sub(r'\{(\w+)\}', repl, raw)
        else:
            scene : "DrawingScene" = self.scene()
            if scene and scene.hasProperty(name):
                return scene.getPropertyValue(name)
        logger().warning(f"Property '{name}' not found")
        return None

    def setPropertyValue(self : Self, name : str, value : Any) -> bool:
        """
        Set the value of a property.
        Returns True if the property was set, False otherwise.
        """
        if not self.hasProperty(name):
            logger().warning(f"Property '{name}' not found")
            return False
        if name in self._PROPERTY_SPECS:
            spec = self._PROPERTY_SPECS[name]
            if not callable(spec.setter):
                logger().warning(f"Property '{name}' is read-only")
                return False
            spec.setter(self, value)
            return True
        else:
            self._custom_properties[name] = value
            return True

    def initProperty(self : Self, name : str, value : Any) -> bool:
        """
        Initialize a property. Creates if required, and sets the value;
        for use in deserialization, and for creating new custom properties.
        Returns True if the property was initialized, False otherwise.
        """
        if name not in self._PROPERTY_SPECS:
            self._custom_properties[name] = ""
        return self.setPropertyValue(name, value)

    def getPropertyTextValue(
        self : Self,
        name : str,
        pt   : PropertyTextItem
    ) -> str | None:
        """
        Get the value of a property, for a property text;
        ensure that a property signaller exists and is connected.
        Returns the value of the property if found, otherwise None.
        """
        value = self.getPropertyValue(name)
        if value:
            if name not in self._property_signallers:
                self._property_signallers[name] = PropertySignaller()
            property_signaller = self._property_signallers[name]
            property_signaller.changed.connect(pt.onTextChange)
        return value

    def renProperty(self : Self, old_name : str, new_name : str) -> bool:
        """
        Rename a property.
        Returns True if the property was renamed, False otherwise.
        """
        if not self.hasProperty(old_name):
            logger().warning(f"Property '{old_name}' not found")
            return False
        if old_name == new_name:  # no change
            return False
        if self.hasProperty(new_name):
            logger().warning(f"Property '{new_name}' already exists")
            return False
        if old_name in self._PROPERTY_SPECS:
            logger().warning(f"Inherent property '{old_name}' cannot be renamed")
            return False
        self._custom_properties[new_name] = self._custom_properties[old_name]
        del self._custom_properties[old_name]
        return True

    def delProperty(self : Self, name : str) -> bool:
        """
        Delete a property.
        Returns True if the property was deleted, False otherwise.
        """
        if not self.hasProperty(name):
            logger().warning(f"Property '{name}' not found")
            return False
        if name in self._PROPERTY_SPECS:
            logger().warning(f"Inherent property '{name}' cannot be deleted")
            return False
        del self._custom_properties[name]
        if name in self._property_signallers:
            del self._property_signallers[name]
        return True

    def updateProperties(self : Self, names : list[str]) -> None:
        for name in names:
            if name in self._property_signallers:
                self._property_signallers[name].changed.emit()
