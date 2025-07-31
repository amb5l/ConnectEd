__all__ = [
    "PropertySpec",
    "PropertyTextSpec",
    "PropertiesMixin"
]

from typing import Callable, Optional, Any, Self
from dataclasses import dataclass

from PyQt6.QtCore import QPointF

from ...core import logger, val2str,str2val

from .items.key_point import KPLoc

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .items.property_text import PropertyDisplay


@dataclass
class PropertySpec:
    type_name : str                             = "str"
    exists    : Optional[Callable[[], bool]]    = None
    getter    : Optional[Callable[[], Any]]     = None
    setter    : Optional[Callable[[Any], None]] = None
    value     : Optional[Any]                   = None  # for simple strings
    custom    : bool                            = False

    def __post_init__(self):
        # defaults for simple strings
        if self.exists is None:
            self.exists = lambda: True
        if self.getter is None:
            self.getter = lambda self: "" if self.value is None else self.value
        if self.setter is None:
            self.setter = lambda obj, val: setattr(self, 'value', str(val))
            if self.value is None:
                self.value = ""

@dataclass
class PropertyTextSpec:
    display : "PropertyDisplay"
    anchor  : KPLoc
    pos     : QPointF
    cleat   : KPLoc

class PropertiesMixin:
    # class variables
    _PROPERTY_SPECS : dict[str, PropertySpec]
    _PROPERTY_TEXTS : dict[str, PropertyTextSpec]

    # instance variables
    _properties : dict[str, PropertySpec]

    def initProperties(self : Self, bare : bool = False) -> None:
        from .items.property_text import PropertyText
        self._properties = self._PROPERTY_SPECS.copy()
        if not hasattr(self, "_PROPERTY_TEXTS"):
            return
        for name, pts in self._PROPERTY_TEXTS.items():
            p = PropertyText()
            p.setAnchorLoc(pts.anchor)
            p.setPos(pts.pos)
            p.setName(name)
            p.setDisplay(pts.display)
            p.setParentItem(self._key_points[pts.cleat])

    def getPropertyNamesAndValues(self : Self) -> dict[str, str]:
        d = {}
        for name, ps in self._properties.items():
            d[name] = val2str(ps.getter(self))
        return d

    def getPropertyValue(self, name : str) -> str:
        if name not in self._properties:
            logger.warning(f"Property {name} does not exist")
        ps = self._properties[name]
        return val2str(ps.getter(self))

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
        self._properties[name] = PropertySpec(custom=True)

    def deleteProperty(self, name : str) -> None:
        if name in self._properties:
            v = self._properties[name]
            if v.custom:
                del self._properties[name]
        else:
            logger.warning(f"Property {name} does not exist")
