__all__ = [
    "SimplePropertySpec",
    "PropertySpec",
    "PropertyTextSpec",
    "PropertiesMixin"
]

from typing import Callable, Any, Self
from dataclasses import dataclass

from PyQt6.QtCore import QPointF

from ...core import logger

from .items.key_point import KPLoc

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .items.property_text import PropertyDisplay


@dataclass
class SimplePropertySpec:
    value    : str
    inherent : bool

@dataclass
class PropertySpec:
    type_name : str
    exists    : Callable[[], bool]
    getter    : Callable[[], Any]
    setter    : Callable[[Any], None]

@dataclass
class PropertyTextSpec:
    display : "PropertyDisplay"
    anchor  : KPLoc
    pos     : QPointF
    cleat   : KPLoc

class PropertiesMixin:
    # class variables
    _PROPERTY_SPECS : dict[str, PropertySpec | SimplePropertySpec]
    _PROPERTY_TEXTS : dict[str, PropertyTextSpec]

    # instance variables
    _properties : dict[str, PropertySpec | SimplePropertySpec]
    _inherent   : list[str]

    def initProperties(self : Self, bare : bool = False) -> None:
        from .items.property_text import PropertyText
        self._properties = self._PROPERTY_SPECS.copy()
        if not hasattr(self, "_PROPERTY_TEXTS"):
            return
        for name, pts in self._PROPERTY_TEXTS.items():
            p = PropertyText(name, pts.display, pts.pos, pts.anchor)
            p.setParentItem(self.key_points[pts.cleat])

    def getProperty(self, name : str) -> Any:
        if name not in self._properties:
            logger.warning(f"Property {name} does not exist")
        v = self._properties[name]
        return v.getter() if isinstance(v, PropertySpec) else v.value

    def setProperty(self, name : str, value : Any) -> None:
        if name not in self._properties:
            logger.warning(f"Property {name} does not exist")
            return
        v = self._properties[name]
        if isinstance(v, PropertySpec):
            v.setter(value)
        else:
            v.value = value

    def addProperty(self, name : str) -> None:
        if name in self._properties:
            logger.warning(f"Property {name} already exists")
            return
        self._properties[name] = SimplePropertySpec(value="", inherent=False)

    def deleteProperty(self, name : str) -> None:
        if name in self._properties:
            v = self._properties[name]
            if isinstance(v, SimplePropertySpec):
                if not v.inherent:
                    del self._properties[name]
        else:
            logger.warning(f"Property {name} does not exist")
