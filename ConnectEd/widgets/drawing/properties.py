__all__ = [
    "SimplePropertySpec",
    "PropertySpec",
    "PropertyTextSpec",
    "PropertiesMixin"
]

from typing import Callable, Any, Self
from dataclasses import dataclass

from PyQt6.QtCore import QPointF

from ...core import logger, val2str,str2val

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

    def getPropertyNamesAndValues(self : Self) -> dict[str, str]:
        d = {}
        for name, ps in self._properties.items():
            d[name] = val2str(ps.getter(self)) if isinstance(ps, PropertySpec) \
                else ps.value
        return d

    def getPropertyValue(self, name : str) -> str:
        if name not in self._properties:
            logger.warning(f"Property {name} does not exist")
        ps = self._properties[name]
        return val2str(ps.getter(self)) if isinstance(ps, PropertySpec) \
            else ps.value

    def setPropertyValue(self, name : str, value : str) -> None:
        if name not in self._properties:
            logger.warning(f"Property {name} does not exist")
            return
        ps = self._properties[name]
        if isinstance(ps, PropertySpec):
            ps.setter(self, str2val(value, ps.type_name))
        else:
            ps.value = value

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
