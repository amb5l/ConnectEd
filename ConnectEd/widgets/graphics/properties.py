from typing import Callable, Optional, Any, Self
from dataclasses import dataclass

from ...app import logger

from ...core.utils import val2str

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .views.drawing import DrawingView
    from .items.property_text import PropertyText, PropertyTextSpec


@dataclass
class PropertySpec:
    type_name   : str                             = "str"
    exists      : Optional[Callable[[], bool]]    = None
    getter      : Optional[Callable[[], Any]]     = None
    setter      : Optional[Callable[[Any], None]] = None  # None = read only
    default     : Optional[Callable[[], Any]]     = None  # for when the value is DEFAULT
    description : str                             = ""
    custom      : bool                            = False

    def __post_init__(self):
        # Set defaults for optional functions
        if self.exists is None:
            self.exists = lambda: True
        if self.default is None:
            self.default = lambda: None

class PropertiesMixin:
    # class attributes
    _PROPERTY_SPECS : dict[str, PropertySpec]
    _PROPERTY_TEXTS : dict[str, "PropertyTextSpec"]

    # instance attributes
    _properties : dict[str, PropertySpec]

    def initProperties(self : Self, bare : bool = False) -> None:
        self._properties = self._PROPERTY_SPECS.copy()
        if hasattr(self.__class__, "_getPropertyTexts"):
            property_texts = self.__class__._getPropertyTexts()
        elif hasattr(self, "_PROPERTY_TEXTS"):
            property_texts = self._PROPERTY_TEXTS
        else:
            return
        for name, pts in property_texts.items():
            p : "PropertyText" = pts._class()
            p.setOriginAPName(pts.anchor)
            p.setPos(pts.pos)
            p.setName(name)
            p.setDisplay(pts.display)
            p.setParentItem(self._anchor_points[pts.cleat])

    def getPropertySpec(self : Self, name : str) -> PropertySpec:
        return self._properties[name]

    def renameProperty(self : Self, old : str, new : str) -> None:
        if old == new:
            return
        if old not in self._properties:
            logger().warning(f"Property {old} does not exist")
            return
        if new in self._properties:
            logger().warning(f"Property {new} already exists")
            return
        new_dict = {}
        for name, ps in self._properties.items():
            new_dict[new if name == old else name] = ps
        self._properties = new_dict

    def getPropertyNames(self : Self) -> list[str]:
        return list(self._properties.keys())

    def getPropertyNamesAndValues(self : Self) -> dict[str, str]:
        d = {}
        for name, ps in self._properties.items():
            d[name] = val2str(ps.getter(self))
        return d

    def getPropertyValue(self, name : str) -> Any:
        if name not in self._properties:
            logger().warning(f"Property {name} does not exist")
        ps = self._properties[name]
        return ps.getter(self)

    def setPropertyValue(self, name : str, value : Any) -> None:
        if name not in self._properties:
            logger().warning(f"Property {name} does not exist")
            return
        ps = self._properties[name]
        if ps.setter is not None:
            ps.setter(self, value)
        else:
            logger().warning(f"Property {name} is read only")
        self.onPropertyChange()

    def getPropertyDescription(self, name : str) -> str:
        if name not in self._properties:
            logger().warning(f"Property {name} does not exist")
        ps = self._properties[name]
        return ps.description

    def setPropertyDescription(self, name : str, description : str) -> None:
        if name not in self._properties:
            logger().warning(f"Property {name} does not exist")
            return
        ps = self._properties[name]
        ps.description = description

    def addProperty(self, name : str) -> None:
        if name in self._properties:
            logger().warning(f"Property {name} already exists")
            return
        self._properties[name] = PropertySpec(custom=True)

    def deleteProperty(self, name : str) -> None:
        if name in self._properties:
            v = self._properties[name]
            if v.custom:
                del self._properties[name]
        else:
            logger().warning(f"Property {name} does not exist")

    def onPropertyChange(self) -> None:
        """Notify all PropertyText children to refresh their display."""
        from PyQt6.QtWidgets import QGraphicsScene
        if isinstance(self, QGraphicsScene):
            children = self.items()  # QGraphicsScene uses items()
        else:
            children = self.childItems()  # QGraphicsItem uses childItems()
        for child in children:
            if hasattr(child, "onTextChange"):
                child.onTextChange()
            if hasattr(child, "childItems"):
                for grandchild in child.childItems():
                    if hasattr(grandchild, "onTextChange"):
                        grandchild.onTextChange()

    def ctxMenuProperties(
        self    : Self,
        checked : bool,
        view    : "DrawingView"
    ) -> None:
        view.editProperties(self)
