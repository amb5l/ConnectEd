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
                self, name, spec.type_name, spec.getter, spec.setter
            )
            if spec.text is not None:
                property_text = PropertyText(
                    name,
                    spec.text.anchor,
                    spec.text.pos,
                    spec.text.origin,
                    spec.text.display
                )
                property_text.setParentItem(self.getHandle(spec.text.anchor))
                self.properties[name].setText(property_text)

    def initProperty(self : Self, name : str, value : str) -> None:
        """
        Create or update a property. Useful for XML deserialisation.
        """
        if name not in self.properties:
            type_name = self._PROPERTY_SPECS[name].type_name \
                if name in self._PROPERTY_SPECS else "str"
            self.properties[name] = Property(self, name, type_name, value, None)
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

#    def getPropertyNames(self : Self) -> list[str]:
#        return \
#            list(self._PROPERTY_SPECS.keys()) + \
#            list(self._custom_properties.keys())
#
#    def getCustomPropertyNames(self : Self) -> list[str]:
#        return list(self._custom_properties.keys())
#
#    def getPropertyNamesAndValues(self : Self) -> dict[str, str]:
#        return {
#            name: val2str(self.getPropertyValue(name)) \
#                for name in self.getPropertyNames()
#        }
#
#    def hasProperty(self : Self, name : str) -> bool:
#        return name in self._PROPERTY_SPECS or name in self._custom_properties
#
#    def isPropertyCustom(self : Self, name : str) -> bool:
#        return name in self._custom_properties
#
#    def isPropertyReadOnly(self : Self, name : str) -> bool:
#        if name in self._PROPERTY_SPECS:
#            return self._PROPERTY_SPECS[name].setter is None
#        elif name in self._custom_properties:
#            return False
#        else:
#            logger().error(f"Property '{name}' not found")
#            return True
#
#    def getPropertyValue(self : Self, name : str) -> Any:
#        if name in self._PROPERTY_SPECS:
#            if self._PROPERTY_SPECS[name].getter is None:
#                logger().error(f"Property '{name}' has no getter")
#                return None
#            return self._PROPERTY_SPECS[name].getter(self)
#        elif name in self._custom_properties:
#            return self._custom_properties[name]
#        else:
#            logger().error(f"Property '{name}' not found")
#        return None
#
#    def getPropertyDefault(self : Self, name : str) -> Any:
#        if name in self._PROPERTY_SPECS \
#        and self._PROPERTY_SPECS[name].default is not None:
#            return self._PROPERTY_SPECS[name].default(self)
#        else:
#            return None
#
#    def getPropertyTypeName(self : Self, name : str) -> str | None:
#        if name in self._PROPERTY_SPECS:
#            return self._PROPERTY_SPECS[name].type_name
#        elif name in self._custom_properties:
#            return "str"
#        else:
#            logger().error(f"Property '{name}' not found")
#            return None
#
#    def setPropertyValue(self : Self, name : str, value : Any) -> None:
#        if name in self._PROPERTY_SPECS:
#            if self._PROPERTY_SPECS[name].setter is None:
#                logger().error(f"Property '{name}' is read only")
#                return
#            if isinstance(value, str):  # convert string if needed
#                type_name = self._PROPERTY_SPECS[name].type_name
#                if type_name != "str":
#                    value = str2val(value, type_name)
#            self._PROPERTY_SPECS[name].setter(self, value)
#        elif name in self._custom_properties:
#            self._custom_properties[name] = value
#        else:
#            logger().error(f"Property '{name}' not found")
#        if name in self._property_texts:
#            self._property_texts[name].onTextChange()
#
#    def initProperty(self : Self, name : str, value : str) -> None:
#        """Add or update a property."""
#        if self.hasProperty(name):
#            self.setPropertyValue(name, value)
#        else:
#            self.addProperty(name, value)
#
#    def addProperty(self : Self, name : str, value : str) -> None:
#        if name in self._PROPERTY_SPECS:
#            logger().error(f"Inherent property '{name}' already exists")
#            return
#        if name in self._custom_properties:
#            logger().error(f"Custom property '{name}' already exists")
#            return
#        self._custom_properties[name] = value
#
#    def delProperty(self : Self, name : str) -> None:
#        if name in self._PROPERTY_SPECS:
#            logger().error(f"Inherent property '{name}' cannot be deleted")
#            return
#        if name not in self._custom_properties:
#            logger().error(f"Custom property '{name}' not found")
#            return
#        del self._custom_properties[name]
#
#    def renProperty(self : Self, old_name : str, new_name : str) -> None:
#        if old_name == new_name:  # no change
#            return
#        if old_name in self._PROPERTY_SPECS:
#            logger().error(f"Inherent property '{old_name}' cannot be renamed")
#            return
#        if old_name not in self._custom_properties:
#            logger().error(f"Custom property '{old_name}' not found")
#            return
#        # rename
#        self._custom_properties[new_name] = self._custom_properties[old_name]
#        del self._custom_properties[old_name]
#        # handle existing property text, if applicable
#        if old_name in self._property_texts:
#            self._property_texts[new_name] = self._property_texts[old_name]
#            del self._property_texts[old_name]
#            self._property_texts[new_name].setName(new_name)
#
#    def getPropertyTexts(self : Self) -> dict[str, "PropertyText"]:
#        return self._property_texts
#
#    def getPropertyText(self : Self, name : str) -> "PropertyText | None":
#        if name in self._property_texts:
#            return self._property_texts[name]
#        else:
#            return None
#
#    def getPropertyTextTypeName(self : Self, name : str) -> str | None:
#        if name in self._PROPERTY_SPECS:
#            if self._PROPERTY_SPECS[name].text is not None:
#                return self._PROPERTY_SPECS[name].text.cls.__name__
#        return "PropertyText"
#
#    def addPropertyText(self : Self, name : str, pt : "PropertyText") -> None:
#        if name in self._property_texts:
#            logger().error(f"Property text '{name}' already exists")
#            return
#        if name not in self._PROPERTY_SPECS \
#        and name not in self._custom_properties:
#            logger().error(f"Property '{name}' not found")
#            return
#        self._property_texts[name] = pt
#
#    def delPropertyText(self : Self, name : str) -> None:
#        if name not in self._property_texts:
#            logger().error(f"Property text '{name}' not found")
#        del self._property_texts[name]
