from typing import Callable, Any, Self
from dataclasses import dataclass

from ...app import logger

from ...core.utils import val2str

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .views.drawing import DrawingView
    from .items.property_text import PropertyText, PropertyTextSpec


@dataclass
class PropertySpec:
    type_name   : str                          = "str"
    exists      : Callable[[], bool] | None    = None
    getter      : Callable[[], Any] | None     = None
    setter      : Callable[[Any], None] | None = None  # None = read only
    default     : Callable[[], Any] | None     = None  # for when the value is DEFAULT
    description : str                          = ""
    custom      : bool                         = False

    def __post_init__(self : Self):
        # Set defaults for optional functions
        if self.exists is None:
            self.exists = lambda instance: True
        if self.default is None:
            self.default = lambda instance: None


class PropertiesMixin:
    # class attributes
    _PROPERTY_SPECS : dict[str, PropertySpec]
    _PROPERTY_TEXTS : dict[str, "PropertyTextSpec"]

    # instance attributes
    _property_specs : dict[str, PropertySpec]
    _property_texts : dict[str, "PropertyText"]

    def initProperties(self : Self, bare : bool = False) -> None:
        self._property_specs = self._PROPERTY_SPECS.copy()
        if bare:
            return
        if hasattr(self.__class__, "_getPropertyTexts"):
            property_texts = self.__class__._getPropertyTexts()
        elif hasattr(self, "_PROPERTY_TEXTS"):
            property_texts = self._PROPERTY_TEXTS
        else:
            return
        self._property_texts = {}
        for name, pts in property_texts.items():
            p : "PropertyText" = pts._class()
            p.setOriginAPName(pts.anchor)
            p.setPos(pts.pos)
            p.setName(name)
            p.setDisplay(pts.display)
            p.setParentItem(self._anchor_points[pts.cleat])
            self._property_texts[name] = p

    def getPropertySpec(self : Self, name : str) -> PropertySpec:
        return self._property_specs[name]

    def renameProperty(self : Self, old : str, new : str) -> None:
        if old == new:
            return
        if old not in self._property_specs:
            logger().warning(f"Property {old} does not exist")
            return
        if new in self._property_specs:
            logger().warning(f"Property {new} already exists")
            return
        new_dict = {}
        for name, ps in self._property_specs.items():
            new_dict[new if name == old else name] = ps
        self._property_specs = new_dict

    def getPropertyNames(self : Self) -> list[str]:
        return list(self._property_specs.keys())

    def getPropertyNamesAndValues(self : Self) -> dict[str, str]:
        d = {}
        for name, ps in self._property_specs.items():
            if ps.exists(self):
                d[name] = val2str(ps.getter(self))
        return d

    def getPropertyValue(self : Self, name : str) -> Any:
        if name not in self._property_specs:
            logger().warning(f"Property {name} does not exist")
            return None
        ps = self._property_specs[name]
        if not ps.exists(self):
            logger().warning(f"Property {name} does not exist for this instance")
            return None
        return ps.getter(self)

    def setPropertyValue(self : Self, name : str, value : Any) -> None:
        if name not in self._property_specs:
            logger().warning(f"Property {name} does not exist")
            return
        ps = self._property_specs[name]
        if not ps.exists(self):
            logger().warning(f"Property {name} does not exist for this instance")
            return
        if ps.setter is not None:
            ps.setter(self, value)
        else:
            logger().warning(f"Property {name} is read only")
        self.onPropertyChange()

    def getPropertyDescription(self : Self, name : str) -> str:
        if name not in self._property_specs:
            logger().warning(f"Property {name} does not exist")
        ps = self._property_specs[name]
        return ps.description

    def setPropertyDescription(self : Self, name : str, description : str) -> None:
        if name not in self._property_specs:
            logger().warning(f"Property {name} does not exist")
            return
        ps = self._property_specs[name]
        ps.description = description

    def addProperty(self : Self, name : str) -> None:
        if name in self._property_specs:
            logger().warning(f"Property {name} already exists")
            return
        self._property_specs[name] = PropertySpec(custom=True)

    def deleteProperty(self : Self, name : str) -> None:
        if name in self._property_specs:
            v = self._property_specs[name]
            if v.custom:
                del self._property_specs[name]
        else:
            logger().warning(f"Property {name} does not exist")

    def getPropertyText(self : Self, name : str) -> "PropertyText":
        return self._property_texts[name]

    def onPropertyChange(self : Self) -> None:
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
