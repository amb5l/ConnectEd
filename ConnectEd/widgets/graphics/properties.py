from typing import Self

from ...app import logger

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
        from .items.property_text import PropertyText
        self.properties = {}
        for name, spec in self._PROPERTY_SPECS.items():
            self.properties[name] = Property(
                self, name, spec.kind, spec.getter, spec.setter
            )
            if spec.text is not None:
                property_text = PropertyText(
                    name,
                    spec.text.anchor,
                    spec.text.pos,
                    spec.text.origin
                )
                property_text.setParentItem(self.getHandle(spec.text.anchor))
                self.properties[name].setText(property_text)

    def initProperty(self : Self, name : str, value : str) -> None:
        """
        Create or update a property. Useful for XML deserialisation.
        """
        from .property import Property
        if name not in self.properties:
            kind = self._PROPERTY_SPECS[name].kind \
                if name in self._PROPERTY_SPECS else "str"
            self.properties[name] = Property(self, name, kind, value, None)
        else:
            self.properties[name].set(value)

    def renProperty(self : Self, old_name : str, new_name : str) -> bool:
        if old_name not in self.properties:
            logger().error(f"Property '{old_name}' not found")
            return False
        if old_name == new_name:  # no change
            return False
        if new_name in self.properties:
            logger().error(f"Property '{new_name}' already exists")
            return False
        if not self.properties[old_name].isStatic():
            logger().error(f"Inherent property '{old_name}' cannot be renamed")
            return False
        self.properties[new_name] = self.properties[old_name]
        del self.properties[old_name]
        return True
