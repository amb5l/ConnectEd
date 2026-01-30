"""
Properties System
=================

The properties system provides access to important attributes of items and
scenes, to facilitate...
- serialization and deserialization (to/from XML);
- tabular editing (dialogs and spreadsheets);
- adding user defined (custom) values.

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

from typing          import Self, Any, Literal, NamedTuple
from dataclasses     import dataclass
from collections.abc import Callable
from enum            import Enum

import re

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui  import QColor

from ...app  import logger
from ...core import Text

from .items import ItemType, Default, DEFAULT, NoChange, NO_CHANGE, AlignH, AlignV


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .scenes.drawing import DrawingScene
    from .items.property_text import PropertyTextSpec, PropertyTextItem
    Owner = ItemType | DrawingScene


@dataclass
class PropertyTextSpec:
    visible   : bool             = True
    cleat     : str | None       = None
    pos_x     : float            = 0
    pos_y     : float            = 0
    origin    : str              = "Top Left"
    align_h   : AlignH           = AlignH.LEFT
    align_v   : AlignV           = AlignV.TOP
    width     : float | None     = None
    height    : float | None     = None
    color     : QColor | Default = DEFAULT
    family    : str    | Default = DEFAULT
    size      : float  | Default = DEFAULT
    bold      : bool   | Default = DEFAULT
    italic    : bool   | Default = DEFAULT
    underline : bool   | Default = DEFAULT

    def astuple(self : Self) -> tuple:
        return (
            self.visible, self.cleat, self.pos_x, self.pos_y, self.origin,
            self.align_h, self.align_v, self.width, self.height,
            self.color, self.family, self.size, self.bold, self.italic, self.underline
        )


class PropertyNotifier(QObject):
    changed = pyqtSignal()


@dataclass
class BaseProperty:
    notifier : PropertyNotifier                     | None  = None
    text     : "PropertyTextSpec | PropertyTextItem | None" = None


@dataclass
class InherentProperty(BaseProperty):
    type_name : str                                              = "str"
    valid     : Literal[True] | Callable[["Owner"], bool] | None = True
    getter    : Callable[["Owner"], Any]                  | None = None
    setter    : Callable[["Owner", Any], None]            | None = None
    default   : Callable[["Owner"], Any]                  | None = None


@dataclass
class CustomProperty(BaseProperty):
    value : Text | None = None


class PropertyDisplay(Enum):
    NONE = "<none>"
    SHOW = "Line"
    HIDE = "Block"


@dataclass
class PropertyState:
    name      : str
    value     : Any
    display   : PropertyDisplay
    cleat     : str    | None = None
    x         : float  | None = None
    y         : float  | None = None
    origin    : str    | None = None
    align_h   : AlignH | None = None
    align_v   : AlignV | None = None
    width     : float  | None = None
    height    : float  | None = None
    color     : QColor | None = None
    family    : str    | None = None
    size      : float  | None = None
    bold      : bool   | None = None
    italic    : bool   | None = None
    underline : bool   | None = None

    @classmethod
    def fromProperty(cls : Self, object : "PropertiesMixin", name : str) -> Self:
        inst = cls(
            name      = name,
            value     = object.getPropertyValue(name),
            display   = object.getPropertyDisplay(name)
        )
        pt = object.getPropertyText(name)
        if pt is not None:
            inst.cleat     = pt.cleat(name),
            inst.x         = pt.x(name),
            inst.y         = pt.y(name),
            inst.origin    = pt.origin(name),
            inst.align_h   = pt.alignH(name),
            inst.align_v   = pt.alignV(name),
            inst.width     = pt.width(name),
            inst.height    = pt.height(name),
            inst.color     = pt.quillColor(name),
            inst.family    = pt.quillFamily(name),
            inst.size      = pt.quillSize(name),
            inst.bold      = pt.quillBold(name),
            inst.italic    = pt.quillItalic(name),
            inst.underline = pt.quillUnderline(name)
        return inst


@dataclass
class PropertyChange:
    name      : str             | NoChange = NO_CHANGE
    value     : Any             | NoChange = NO_CHANGE
    display   : PropertyDisplay | NoChange = NO_CHANGE
    cleat     : str             | NoChange = NO_CHANGE
    x         : float           | NoChange = NO_CHANGE
    y         : float           | NoChange = NO_CHANGE
    origin    : str             | NoChange = NO_CHANGE
    align_h   : AlignH          | NoChange = NO_CHANGE
    align_v   : AlignV          | NoChange = NO_CHANGE
    width     : float | None    | NoChange = NO_CHANGE
    height    : float | None    | NoChange = NO_CHANGE
    color     : QColor          | NoChange = NO_CHANGE
    family    : str             | NoChange = NO_CHANGE
    size      : float           | NoChange = NO_CHANGE
    bold      : bool            | NoChange = NO_CHANGE
    italic    : bool            | NoChange = NO_CHANGE
    underline : bool            | NoChange = NO_CHANGE


class PropertyEdit(NamedTuple):
    name  : str | None                             # (old) name or None for new
    after : PropertyChange | PropertyState | None  # change | add | delete


class PropertiesMixin:
    # class attributes
    _PROPERTIES : dict[str, InherentProperty]

    # instance attributes
    _properties : dict[str, InherentProperty | CustomProperty]

    def initProperties(self : Self, fresh : bool) -> None:
        """
        Initialize the properties system for this instance.
        """
        # make shallow copy of _PROPERTIES
        self._properties = dict(self._PROPERTIES)
        if not fresh:
            return
        # convert PropertyTextSpec instances to PropertyTextItem instances
        for name, property in self._properties.items():
            spec = property.text
            if isinstance(spec, PropertyTextSpec):
                self.addPropertyText(name, *spec.astuple())

    def getPropertyNames(self : Self) -> list[str]:
        return list(self._properties.keys())

    def hasProperty(self : "Self | Owner", name : str) -> bool:
        """
        Test property existance.
        Returns True if the property exists, False otherwise.
        """
        return hasattr(self, "_properties") and name in self._properties

    def isPropertyInherent(self : Self, name : str) -> bool | None:
        """
        Test if a property is inherent.
        Returns True if the property is inherent, False otherwise.
        """
        # check property existence
        if not self.hasProperty(name):
            logger().warning(f"Property '{name}' not found")
            return None
        # get property instance
        property = self._properties[name]
        # test if inherent
        return isinstance(property, InherentProperty)

    def isPropertyReadOnly(self : Self, name : str) -> bool | None:
        """
        Test if a property is read-only.
        Returns True if the property is read-only, False otherwise.
        """
        # check property existence
        if not self.hasProperty(name):
            logger().warning(f"Property '{name}' not found")
            return None
        # get property instance
        property = self._properties[name]
        # test if read-only
        return isinstance(property, InherentProperty) and not callable(property.setter)

    def getPropertyTypeName(self : Self, name : str) -> str | None:
        # check property existence
        if not self.hasProperty(name):
            logger().warning(f"Property '{name}' not found")
            return None
        # get property instance
        property = self._properties[name]
        # return type name
        return property.type_name if isinstance(property, InherentProperty) else "Text"

    def getPropertyValid(self : Self, name : str) -> bool:
        """
        Test if a property is valid.
        Returns True if the property is valid, False otherwise.
        """
        # check property existence
        if not self.hasProperty(name):
            logger().warning(f"Property '{name}' not found")
            return None
        # get validity
        property = self._properties[name]
        if isinstance(property, InherentProperty):
            return property.valid is True or \
                (callable(property.valid) and property.valid(self))
        elif isinstance(property, CustomProperty):
            return True
        else:
            logger().warning(f"Bad property type: {type(property)}")
            return False

    def getPropertyDefault(self : Self, name : str) -> Any:
        """
        Get the default value of a property.
        Returns the default value of the property if found, None otherwise.
        """
        # check property existence
        if not self.hasProperty(name):
            logger().warning(f"Property '{name}' not found")
            return None
        # get property instance
        property = self._properties[name]
        # get default value
        if isinstance(property, InherentProperty) and callable(property.default):
            return property.default(self)
        # not found
        return None

    def getPropertyValue(
        self   : Self,
        name   : str,
        slot   : Callable  | None = None,  # e.g. PropertyTextItem.onTextChange
        trail  : list[str] | None = None   # substitution recursion trail
    ) -> Any:
        """
        Get the value of a property. Supports substitution of other properties;
        for items these can be scene properties.
        If a slot is provided, ensures that a property notifier exists and is
        connected to it.
        Returns the value of the property if found, otherwise None.
        """
        # check property existence
        if not self.hasProperty(name):
            logger().warning(f"Property '{name}' not found: {trail}")
            return None
        # detect recursion issues
        if trail is not None:  # substitution is enabled
            if name in trail:
                logger().warning(
                    f"Property '{name}' substitution recursion loop detected: {trail}"
                )
                return None
            trail = trail + [name]
            if len(trail) > 10:
                logger().warning(
                    f"Property substitution recursion depth exceeded: {trail}"
                )
                return None
        # get property instance
        property = self._properties[name]
        # if slot is specified, connect the notifier to it
        if slot:
            # ensure that a notifier exists
            property.notifier = property.notifier or PropertyNotifier()
            # avoid duplicate connections
            try:
                property.notifier.changed.disconnect(slot)
            except TypeError:
                pass
            property.notifier.changed.connect(slot)
        # inherent properties
        if isinstance(property, InherentProperty):
            if not callable(property.getter):
                logger().warning(f"Property '{name}' has no getter: {trail}")
                return None
            else:
                return property.getter(self)
        # custom properties
        elif isinstance(property, CustomProperty):
            if trail is None:  # substitution is disabled
                return property.value
             # substitution
            def repl(match: re.Match) -> str:
                var_name = match.group(1)
                # look locally, then (for items) in the scene
                if self.hasProperty(var_name):
                    return str(self.getPropertyValue(var_name, slot, trail))
                elif hasattr(self, "scene"):
                    scene : "DrawingScene | None" = self.scene()
                    if scene and scene.hasProperty(var_name):
                        return str(scene.getPropertyValue(var_name, slot, trail))
                return f"{var_name}>"  # unresolved substitution
            return Text(
                re.sub(r'\{(\w+)\}', repl, property.value.string),
                property.value.block
            )
        # unknown properties
        logger().warning(f"Property '{name}' has unknown type: {type(property)}")
        return None

    def setPropertyValue(self : Self, name : str, value : Any) -> bool:
        """
        Set the value of a property.
        Returns True if the property was set, False otherwise.
        """
        # check property existence
        if not self.hasProperty(name):
            logger().warning(f"Property '{name}' not found")
            return False
        property = self._properties[name]
        # inherent properties
        if isinstance(property, InherentProperty):
            if not callable(property.setter):
                logger().warning(f"Property '{name}' is read-only")
                return False
            property.setter(self, value)
        # custom properties
        elif isinstance(property, CustomProperty):
            if isinstance(value, Text):
                property.value = value
            else:
                logger().warning(f"Bad property value type: {type(value)}")
                return False
        # unknown properties
        else:
            logger().warning(f"Bad property type: {type(property)}")
            return False
        if property.notifier:
            property.notifier.changed.emit()
        return True

    def initProperty(self : Self, name : str, value : Any) -> bool:
        """
        Initialize a property. Creates if required, and sets the value;
        for use in deserialization, and for creating new custom properties.
        Returns True if the property was initialized, False otherwise.
        """
        if self.hasProperty(name):
            self.addProperty(name, value)
        else:
            return self.setPropertyValue(name, value)

    def addProperty(
        self      : Self,
        name      : str,
        value     : Text,
        display   : PropertyDisplay = PropertyDisplay.NONE,
        cleat     : str              | None = None,
        x         : float            | None = None,
        y         : float            | None = None,
        align_h   : AlignH           | None = None,
        align_v   : AlignV           | None = None,
        width     : float            | None = None,
        height    : float            | None = None,
        color     : QColor | Default | None = None,
        family    : str    | Default | None = None,
        size      : float  | Default | None = None,
        bold      : bool   | Default | None = None,
        italic    : bool   | Default | None = None,
        underline : bool   | Default | None = None,
        origin : str = "Top Left",
    ) -> bool:
        """
        Add a property.
        Returns True if the property was added, False otherwise.
        """
        # check for existing property
        if self.hasProperty(name):
            logger().warning(f"Property '{name}' already exists")
            return False
        # create custom property
        self._properties[name] = CustomProperty(value=value)
        # add property text if required
        if display != PropertyDisplay.NONE:
            visible = display == PropertyDisplay.SHOW
            pt_args = {
                k: v for k, v in locals().items() \
                    if k in PropertyTextSpec.__dataclass_fields__.keys()
                        and k != "visible"
            }
            self.addPropertyText(name, **pt_args)
        return True

    def renProperty(self : Self, old_name : str, new_name : str) -> bool:
        """
        Rename a property.
        Returns True if the property was renamed, False otherwise.
        """
        # check for existing property
        if not self.hasProperty(old_name):
            logger().warning(f"Property '{old_name}' not found")
            return False
        # check for no change
        if old_name == new_name:
            return False
        # check for clash with existing property
        if self.hasProperty(new_name):
            logger().warning(f"Property '{new_name}' already exists")
            return False
        # get property instance
        property = self._properties[old_name]
        # check if inherent
        if isinstance(property, InherentProperty):
            logger().warning(f"Cannot rename inherent property '{old_name}'")
            return False
        # rename
        self._properties[new_name] = property
        del self._properties[old_name]
        return True

    def delProperty(self : Self, name : str) -> bool:
        """
        Remove a property.
        Returns True if the property was removed, False otherwise.
        """
        # check property existence
        if not self.hasProperty(name):
            logger().warning(f"Property '{name}' not found")
            return False
        # get property instance
        property = self._properties[name]
        # check if inherent
        if isinstance(property, InherentProperty):
            logger().warning(f"Inherent property '{name}' cannot be removed")
            return False
        # remove text
        property.text.setParentItem(None)
        property.text.scene().removeItem(property.text)
        property.text = None
        # cache notifier reference
        notifier = property.notifier
        # remove property from dictionary
        del self._properties[name]
        # notify property receivers
        if notifier:
            notifier.changed.emit()
        # done
        return True

    def signalPropertyChanges(self : Self, names : str | list[str]) -> None:
        if not hasattr(self, "_properties"):
            return  # not yet initialized
        if isinstance(names, str):
            names = [names]
        for name in names:
            if self.hasProperty(name):
                property = self._properties[name]
                if property.notifier:
                    property.notifier.changed.emit()

    def getPropertyDisplay(self : Self, name : str) -> PropertyDisplay:
        from .items.property_text import PropertyTextItem
        # check property existence
        if not self.hasProperty(name):
            logger().warning(f"Property '{name}' not found")
            return PropertyDisplay.NONE
        # get property instance
        property = self._properties[name]
        # get text item
        pt = property.text
        if not isinstance(pt, PropertyTextItem):
            return PropertyDisplay.NONE
        return PropertyDisplay.SHOW if pt.isVisible() else PropertyDisplay.HIDE

    def getPropertyText(self : Self, name : str) -> "PropertyTextItem | None":
        # check property existence
        if not self.hasProperty(name):
            logger().warning(f"Property '{name}' not found")
            return None
        # return PropertyTextItem instance
        return self._properties[name].text

    def setPropertyText(self : Self, name : str, text : "PropertyTextItem") -> bool:
        """
        Set a property text.
        """
        # check property existence
        if not self.hasProperty(name):
            logger().warning(f"Property '{name}' not found")
            return False
        # get property instance
        property = self._properties[name]
        # set property text
        property.text = text
        return True

    def addPropertyText(
        self      : Self,
        name      : str,
        visible   : bool             = True,
        cleat     : str              = "Bottom Left",
        x         : float            = 0,
        y         : float            = 0,
        origin    : str              = "Top Left",
        align_h   : AlignH           = AlignH.LEFT,
        align_v   : AlignV           = AlignV.TOP,
        width     : float | None     = None,
        height    : float | None     = None,
        color     : QColor | Default = DEFAULT,
        family    : str    | Default = DEFAULT,
        size      : float  | Default = DEFAULT,
        bold      : bool   | Default = DEFAULT,
        italic    : bool   | Default = DEFAULT,
        underline : bool   | Default = DEFAULT
    ) -> bool:
        """
        Add a property text.
        Returns True if the property text was added, False otherwise.
        """
        from .items.property_text import PropertyTextItem
        # check property existence
        if not self.hasProperty(name):
            logger().warning(f"Property '{name}' not found")
            return False
        # get property instance
        property = self._properties[name]
        # check for existing PropertyTextItem
        if isinstance(property.text, PropertyTextItem):
            logger().warning(f"Property '{name}' already has text")
            return False
        # create new PropertyTextItem
        pt_args = {
            k: v for k, v in locals().items() \
                if k in PropertyTextSpec.__dataclass_fields__.keys()
                    and k != "visible"
        }
        property.text = PropertyTextItem(name, **pt_args, parent=self)
        return True

    def editPropertyText(
        self : Self,
        name      : str,
        visible   : bool         | NoChange = NO_CHANGE,
        cleat     : str          | NoChange = NO_CHANGE,
        x         : float        | NoChange = NO_CHANGE,
        y         : float        | NoChange = NO_CHANGE,
        origin    : str          | NoChange = NO_CHANGE,
        align_h   : AlignH       | NoChange = NO_CHANGE,
        align_v   : AlignV       | NoChange = NO_CHANGE,
        width     : float | None | NoChange = NO_CHANGE,
        height    : float | None | NoChange = NO_CHANGE,
        color     : QColor       | NoChange = NO_CHANGE,
        family    : str          | NoChange = NO_CHANGE,
        size      : float        | NoChange = NO_CHANGE,
        bold      : bool         | NoChange = NO_CHANGE,
        italic    : bool         | NoChange = NO_CHANGE,
        underline : bool         | NoChange = NO_CHANGE
    ) -> bool:
        """
        Edit a property text.
        Returns True if the property text was edited, False otherwise.
        """
        from .items.property_text import PropertyTextItem
        # check property existence
        if not self.hasProperty(name):
            logger().warning(f"Property '{name}' not found")
            return False
        # get property instance
        property = self._properties[name]
        # check PropertyTextItem existence
        if not isinstance(property.text, PropertyTextItem):
            logger().warning(f"Property '{name}' does not have text")
            return False
        # get PropertyTextItem instance
        pt = property.text
        # edit PropertyTextItem
        if visible   is not NO_CHANGE: pt.setVisible(visible)
        if cleat     is not NO_CHANGE: pt.setCleat(cleat)
        if x         is not NO_CHANGE: pt.setX(x)
        if y         is not NO_CHANGE: pt.setY(y)
        if origin    is not NO_CHANGE: pt.setOrigin(origin)
        if align_h   is not NO_CHANGE: pt.setAlignH(align_h)
        if align_v   is not NO_CHANGE: pt.setAlignV(align_v)
        if width     is not NO_CHANGE: pt.setWidth(width)
        if height    is not NO_CHANGE: pt.setHeight(height)
        if color     is not NO_CHANGE: pt.setQuillColor(color)
        if family    is not NO_CHANGE: pt.setQuillFamily(family)
        if size      is not NO_CHANGE: pt.setQuillSize(size)
        if bold      is not NO_CHANGE: pt.setQuillBold(bold)
        if italic    is not NO_CHANGE: pt.setQuillItalic(italic)
        if underline is not NO_CHANGE: pt.setQuillUnderline(underline)
        return True

    def delPropertyText(self : Self, name : str) -> bool:
        """
        Remove a property text.
        Returns True if the property text was removed, False otherwise.
        """
        from .items.property_text import PropertyTextItem
        # check property existence
        if not self.hasProperty(name):
            logger().warning(f"Property '{name}' not found")
            return False
        # get property instance
        property = self._properties[name]
        # check for existing PropertyTextItem
        if not isinstance(property.text, PropertyTextItem):
            logger().warning(f"Property '{name}' does not have text")
            return False
        # unparent PropertyTextItem
        property.text.setParentItem(None)
        # remove from scene
        property.text.scene().removeItem(property.text)
        # remove reference
        property.text = None
        return True
