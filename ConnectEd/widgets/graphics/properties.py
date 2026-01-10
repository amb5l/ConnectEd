from typing      import Self, Any, TypeAlias
from dataclasses import dataclass

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QColor

from ...app import logger

from .items import Default, NoChange, NO_CHANGE, AlignH, AlignV

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .property import Property, PropertySpec


class PropertiesMixin:
    # class attributes
    _PROPERTY_SPECS : dict[str, "PropertySpec"]

    # instance attributes
    properties : dict[str, "Property"]

    def initProperties(self : Self, bare : bool = False) -> None:
        from .property import Property
        from .items.property_text import PropertyTextBlock, PropertyTextLine
        self.properties = {}
        for name, spec in self._PROPERTY_SPECS.items():
            self.properties[name] = Property(
                self,
                name,
                spec.kind,
                spec.valid,
                spec.getter,
                spec.setter,
                spec.default,
                inherent = True
            )
            if not bare and spec.text is not None:
                property_text_cls = PropertyTextBlock if spec.text.block \
                    else PropertyTextLine
                property_text = property_text_cls(
                    name,
                    spec.text.anchor,
                    spec.text.pos,
                    spec.text.origin
                )
                property_text.setParentItem(self.getHandle(spec.text.anchor))
                self.properties[name].setText(property_text)
                property_text.onPropertyChange()  # set text after parenting

    def initProperty(self : Self, name : str, value : str) -> None:
        """
        Create or update a property. Useful for XML deserialisation.
        """
        from .property import Property
        if name not in self.properties:
            if name in self._PROPERTY_SPECS:
                # Use spec's getter/setter so value is applied to item
                s = self._PROPERTY_SPECS[name]
                self.properties[name] = Property(
                    self, name, s.kind, s.valid, s.getter, s.setter, s.default
                )
            else:
                # Dynamic property (no spec) - store as static value
                self.properties[name] = Property(self, name, "str", None, value, None)
        self.properties[name].set(value)

    def renProperty(self : Self, old_name : str, new_name : str) -> bool:
        """
        Rename a property.
        """
        if old_name not in self.properties:
            logger().error(f"Property '{old_name}' not found")
            return False
        if old_name == new_name:  # no change
            return False
        if new_name in self.properties:
            logger().error(f"Property '{new_name}' already exists")
            return False
        if not self.properties[old_name].inherent():
            logger().error(f"Inherent property '{old_name}' cannot be renamed")
            return False
        self.properties[new_name] = self.properties[old_name]
        del self.properties[old_name]
        return True

    def delProperty(self : Self, name : str) -> bool:
        """
        Delete a property.
        """
        if name not in self.properties:
            logger().error(f"Property '{name}' not found")
            return False
        property = self.properties[name]
        property.setText(None)
        del self.properties[name]
        return True
