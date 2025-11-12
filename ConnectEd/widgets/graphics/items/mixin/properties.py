from typing import Self, Any
from collections.abc import Callable
from dataclasses import dataclass

from ...property   import PropertySpec, Property
from ...properties import PropertiesMixin

from .. import ItemType

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..property_text import PropertyTextSpec, PropertyText


@dataclass
class ItemPropertySpec(PropertySpec):
    # owner type = item
    getter    : Callable[[ItemType], Any] | str | None  = None
    setter    : Callable[[ItemType, Any], None] | None  = None
    # additions for ItemProperty
    valid     : Callable[[ItemType], bool]      | None  = None
    default   : Callable[[ItemType], Any]       | None  = None
    text      : "PropertyTextSpec               | None" = None


class ItemProperty(Property):
    # instance attributes
    _valid   : Callable[[ItemType], bool] | None
    _default : Callable[[ItemType], Any] | None
    _text    : "PropertyText | None"

    def __init__(
        self      : Self,
        owner     : ItemType,
        name      : str,
        type_name : str,
        getter    : Callable[[ItemType], Any] | str | None = None,
        setter    : Callable[[ItemType, Any], None] | None = None,
        valid     : Callable[[ItemType], bool] | None = None,
        default   : Callable[[ItemType], Any] | None = None,
        text      : "PropertyText | None" = None
    ) -> None:
        super().__init__(owner, name, type_name, getter, setter)
        self._valid = valid
        self._default = default
        self._text = text

    def valid(self: Self) -> bool:
        """Check if this property is valid for the given owner (e.g., for XML)."""
        return self._valid(self._owner) if self._valid else True

    def default(self: Self) -> Any:
        """Get default value."""
        return self._default(self._owner) if self._default else None

    def getText(self : Self) -> "PropertyText | None":
        return self._text

    def setText(self : Self, text : "PropertyText | None") -> None:
        self._text = text

    def delText(self : Self) -> None:
        self._text = None


class ItemPropertiesMixin(PropertiesMixin):
    # class attributes
    _PROPERTY_CLASS = ItemProperty
    _PROPERTY_SPECS : dict[str, ItemPropertySpec]

    # instance attributes
    properties : dict[str, ItemProperty]

    def initProperties(self: Self, bare : bool = False) -> None:
        """
        Bare means we are building an item from XML so omit custom
        properties and property texts.
        """
        from ..property_text import PropertyText
        PropertiesMixin.initProperties(self, bare)
        for name, spec in self._PROPERTY_SPECS.items():
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
