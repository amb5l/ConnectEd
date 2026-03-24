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

from typing          import Self, Any, Literal, TypeAlias
from collections.abc import Callable
from dataclasses     import dataclass
from copy            import copy

import re

from PyQt6.QtCore import QObject, pyqtSignal, QPointF
from PyQt6.QtGui  import QColor

from ...app  import logger

from ...core.types import DEFAULT, NoChange, NO_CHANGE, AlignH, AlignV, \
                          Color, FontFamily, FontSize, FontBool, DataKind
from ...core.utils import str2val

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .scenes.drawing import DrawingScene
    from .items import ItemType
    from .items.property_text import PropertyTextSpec, PropertyTextItem
    Owner = ItemType | DrawingScene


@dataclass
class PropertyTextSpec:
    visible   : bool       = True
    cleat     : str | None = None
    x         : float      = 0
    y         : float      = 0
    origin    : str        = "Top Left"
    align_h   : AlignH     = AlignH.LEFT
    align_v   : AlignV     = AlignV.TOP
    width     : float      = -1.0
    height    : float      = -1.0
    color     : Color      = DEFAULT
    family    : FontFamily = DEFAULT
    size      : FontSize   = DEFAULT
    bold      : FontBool   = DEFAULT
    italic    : FontBool   = DEFAULT
    underline : FontBool   = DEFAULT

    def astuple(self : Self) -> tuple:
        return (
            self.visible, self.cleat, self.x, self.y, self.origin,
            self.align_h, self.align_v, self.width, self.height,
            self.color, self.family, self.size, self.bold, self.italic, self.underline
        )


class PropertyNotifier(QObject):
    changed = pyqtSignal()


@dataclass
class InherentProperty:
    kind     : DataKind | Callable[["Owner"], DataKind]
    worthy   : Literal[True] | Callable[["Owner"], bool] | None = True
    getter   : Callable[["Owner"], Any]                  | None = None
    setter   : Callable[["Owner", Any], None]            | None = None
    default  : Callable[["Owner"], Any]                  | None = None
    notifier : PropertyNotifier                          | None = None
    text     : PropertyTextItem                          | None = None


_CUSTOM_PROPERTY_KINDS = (
    DataKind.STR, DataKind.TEXT, DataKind.INT, DataKind.FLOAT, DataKind.BOOL
)


CustomPropertyType : TypeAlias = str | int | float | bool


@dataclass
class CustomProperty:
    kind     : DataKind
    value    : CustomPropertyType | None = None
    notifier : PropertyNotifier   | None = None
    text     : PropertyTextItem   | None = None


class PropertiesManager:
    # instance attributes
    _owner : "PropertiesMixin"
    _dict  : dict[str, InherentProperty | CustomProperty]

    def __init__(self : Self, owner : "PropertiesMixin", fresh : bool) -> None:
        """
        Initialize the properties system for this instance.
        """
        self._owner = owner
        # copy each property so per-instance state (e.g. text) is independent
        self._dict = {k: copy(v) for k, v in self._owner._PROPERTIES.items()}
        # Bind before addText: PropertyText callbacks may run during construction
        # and need owner.properties (initProperties assignment happens after __init__).
        self._owner.properties = self
        if not fresh:
            return
        # convert PropertyTextSpec instances to PropertyTextItem instances
        if hasattr(self._owner, "_PROPERTY_TEXTS"):
            for name, spec in self._owner._PROPERTY_TEXTS.items():
                self.addText(name, *spec.astuple())

    def names(self : Self) -> list[str]:
        return list(self._dict.keys())

    def has(self : Self, name : str) -> bool:
        """
        Test property existance.
        Returns True if the property exists, False otherwise.
        """
        return name in self._dict

    def inherent(self : Self, name : str) -> bool | None:
        """
        Test if a property is inherent.
        Returns True if the property is inherent, False otherwise.
        """
        # check property existence
        if not self.has(name):
            logger().warning(f"Property '{name}' not found")
            return None
        # get property instance
        property = self._dict[name]
        # test if inherent
        return isinstance(property, InherentProperty)

    def writeable(self : Self, name : str) -> bool | None:
        """
        Test if a property is writeable.
        Returns True if the property is writeable, False otherwise.
        """
        # check property existence
        if not self.has(name):
            logger().warning(f"Property '{name}' not found")
            return None
        # get property instance
        property = self._dict[name]
        # test if writeable
        return isinstance(property, CustomProperty) or callable(property.setter)

    def kind(self : Self, name : str) -> DataKind | None:
        # check property existence
        if not self.has(name):
            logger().warning(f"Property '{name}' not found")
            return None
        # get property instance
        property = self._dict[name]
        # return kind
        return property.kind(self._owner) if callable(property.kind) \
            else property.kind

    def setKind(self : Self, name : str, kind : DataKind) -> bool:
        """
        Set the kind of a property - allowed for custom properties only.
        Returns True if the property was set, False otherwise.
        """
        # check property existence
        if not self.has(name):
            logger().warning(f"Property '{name}' not found")
            return False
        property = self._dict[name]
        # check property is custom
        if not isinstance(property, CustomProperty):
            logger().warning(f"Property '{name}' is not custom")
            return False
        # set kind
        property.kind = kind
        return True

    def worthy(self : Self, name : str) -> bool:
        """
        Test if a property is worthy of serialization.
        Returns True if the property is worthy, False otherwise.
        """
        # check property existence
        if not self.has(name):
            logger().warning(f"Property '{name}' not found")
            return None
        # get validity
        property = self._dict[name]
        if isinstance(property, InherentProperty):
            return property.worthy is True or \
                (callable(property.worthy) and property.worthy(self._owner))
        elif isinstance(property, CustomProperty):
            return True
        else:
            logger().warning(f"Bad property type: {type(property)}")
            return False

    def default(self : Self, name : str) -> Any:
        """
        Get the default value of a property.
        Returns the default value of the property if found, None otherwise.
        """
        # check property existence
        if not self.has(name):
            logger().warning(f"Property '{name}' not found")
            return None
        # get property instance
        property = self._dict[name]
        # get default value
        if isinstance(property, InherentProperty) and callable(property.default):
            return property.default(self._owner)
        # not found
        return None

    def value(
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
        if not self.has(name):
            logger().warning(f"Property '{name}' not found: {trail}")
            return None
        # detect recursion issues
        if trail is not None:  # substitution in progress
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
        property = self._dict[name]
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
                return property.getter(self._owner)
        # custom properties
        elif isinstance(property, CustomProperty):
            kind = property.kind
            if kind != DataKind.STR and kind != DataKind.TEXT:  # not a string
                return property.value
             # substitution
            def repl(match: re.Match) -> str:
                var_name = match.group(1)
                # look locally, then (for items) in the scene
                if self.has(var_name):
                    return str(self.value(var_name, slot, trail))
                elif hasattr(self._owner, "scene"):
                    scene : "DrawingScene | None" = self._owner.scene()
                    if scene and scene.properties.has(var_name):
                        return str(scene.properties.value(var_name, slot, trail))
                return f"{var_name}>"  # unresolved substitution
            return re.sub(r'\{(\w+)\}', repl, property.value)
        # unknown properties
        logger().warning(f"Property '{name}' has unknown type: {type(property)}")
        return None

    def setValue(self : Self, name : str, value : Any) -> bool:
        """
        Set the value of a property.
        Returns True if the property was set, False otherwise.
        """
        # check property existence
        if not self.has(name):
            logger().warning(f"Property '{name}' not found")
            return False
        property = self._dict[name]
        # get kind
        kind = property.kind
        # inherent properties
        if isinstance(property, InherentProperty):
            if not callable(property.setter):
                logger().warning(f"Property '{name}' is read-only")
                return False
            # convert from str to appropriate type if necessary
            if isinstance(value, str) and kind != DataKind.STR:
                value = str2val(value, kind)
            property.setter(self._owner, value)
        # custom properties
        elif isinstance(property, CustomProperty):
            if isinstance(value, kind.types()):
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

    def init(self : Self, name : str, value : Any) -> bool:
        """
        Initialize a property. Creates if required, and sets the value;
        for use in deserialization, and for creating new custom properties.
        Returns True if the property was initialized, False otherwise.
        """
        f = self.setValue if self.has(name) else self.add
        return f(name, value)

    def add(
        self  : Self,
        name  : str,
        kind  : DataKind,
        value : Any
    ) -> bool:
        """
        Add a property.
        Returns True if the property was added, False otherwise.
        """
        # check for existing property
        if self.has(name):
            logger().warning(f"Property '{name}' already exists")
            return False
        # check kind
        if kind not in _CUSTOM_PROPERTY_KINDS:
            logger().warning(f"Invalid property kind: {kind}")
            return False
        # create custom property
        self._dict[name] = CustomProperty(kind=kind, value=value)
        return True

    def rename(self : Self, old_name : str, new_name : str) -> bool:
        """
        Rename a property.
        Returns True if the property was renamed, False otherwise.
        """
        # check for existing property
        if not self.has(old_name):
            logger().warning(f"Property '{old_name}' not found")
            return False
        # check for no change
        if old_name == new_name:
            return False
        # check for clash with existing property
        if self.has(new_name):
            logger().warning(f"Property '{new_name}' already exists")
            return False
        # get property instance
        property = self._dict[old_name]
        # check if inherent
        if isinstance(property, InherentProperty):
            logger().warning(f"Cannot rename inherent property '{old_name}'")
            return False
        # rename
        self._dict[new_name] = property
        del self._dict[old_name]
        return True

    def delete(self : Self, name : str) -> bool:
        """
        Remove a property (and its associated property text item if applicable).
        Returns True if the property was removed, False otherwise.
        """
        # check property existence
        if not self.has(name):
            logger().warning(f"Property '{name}' not found")
            return False
        # get property instance
        property = self._dict[name]
        # check if inherent
        if isinstance(property, InherentProperty):
            logger().warning(f"Inherent property '{name}' cannot be removed")
            return False
        # remove text
        if property.text is not None:
            property.text.setParentItem(None)
            property.text.scene().removeItem(property.text)
            property.text = None
        # cache notifier reference
        notifier = property.notifier
        # remove property from dictionary
        del self._dict[name]
        # notify property receivers
        if notifier:
            notifier.changed.emit()
        # done
        return True

    def signalChanges(self : Self, names : str | list[str]) -> None:
        if isinstance(names, str):
            names = [names]
        for name in names:
            if self.has(name):
                property = self._dict[name]
                if property.notifier:
                    property.notifier.changed.emit()

    def text(self : Self, name : str) -> "PropertyTextItem | None":
        """
        Get the property text item for a property.
        Returns the property text item if it exists, None otherwise.
        """
        # check property existence
        if not self.has(name):
            logger().warning(f"Property '{name}' not found")
            return None
        # return PropertyTextItem instance
        return self._dict[name].text

    def setText(self : Self, name : str, text : "PropertyTextItem") -> bool:
        """
        Assign an existing property text item to a property.
        """
        # check property existence
        if not self.has(name):
            logger().warning(f"Property '{name}' not found")
            return False
        # get property instance
        property = self._dict[name]
        # set property text
        property.text = text
        return True

    def addText(
        self      : Self,
        name      : str,
        visible   : bool       = True,
        cleat     : str        = "Bottom Left",
        x         : float      = 0,
        y         : float      = 0,
        origin    : str        = "Top Left",
        align_h   : AlignH     = AlignH.LEFT,
        align_v   : AlignV     = AlignV.TOP,
        width     : float      = -1.0,
        height    : float      = -1.0,
        color     : Color      = DEFAULT,
        family    : FontFamily = DEFAULT,
        size      : FontSize   = DEFAULT,
        bold      : FontBool   = DEFAULT,
        italic    : FontBool   = DEFAULT,
        underline : FontBool   = DEFAULT
    ) -> bool:
        """
        Add a property text item. Replace any existing property text item.
        Returns True if the property text was added, False otherwise.
        """
        from .items.property_text import \
            PropertyTextLineItem, PropertyTextBlockItem, PropertyTextItem
        # check property existence
        if not self.has(name):
            logger().warning(f"Property '{name}' not found")
            return False
        # get property instance
        property = self._dict[name]
        # check for existing PropertyTextItem
        if isinstance(property.text, PropertyTextItem):
            logger().warning(f"Property '{name}' already has text")
            return False
        # create new property text item (line or block)
        pt_cls = PropertyTextBlockItem if property.kind == DataKind.TEXT \
            else PropertyTextLineItem
        property.text = pt_cls(
            name      = name,
            cleat     = cleat,
            pos       = QPointF(x, y),
            origin    = origin,
            align_h   = align_h,
            align_v   = align_v,
            width     = width,
            height    = height,
            color     = color,
            family    = family,
            size      = size,
            bold      = bold,
            italic    = italic,
            underline = underline,
            parent    = self._owner
        )
        property.text.setVisible(visible)
        return True

    def editText(
        self : Self,
        name      : str,
        visible   : bool   | NoChange = NO_CHANGE,
        cleat     : str    | NoChange = NO_CHANGE,
        x         : float  | NoChange = NO_CHANGE,
        y         : float  | NoChange = NO_CHANGE,
        rotation  : float  | NoChange = NO_CHANGE,
        flip      : bool   | NoChange = NO_CHANGE,
        origin    : str    | NoChange = NO_CHANGE,
        align_h   : AlignH | NoChange = NO_CHANGE,
        align_v   : AlignV | NoChange = NO_CHANGE,
        width     : float  | NoChange = NO_CHANGE,
        height    : float  | NoChange = NO_CHANGE,
        color     : QColor | NoChange = NO_CHANGE,
        family    : str    | NoChange = NO_CHANGE,
        size      : float  | NoChange = NO_CHANGE,
        bold      : bool   | NoChange = NO_CHANGE,
        italic    : bool   | NoChange = NO_CHANGE,
        underline : bool   | NoChange = NO_CHANGE
    ) -> bool:
        """
        Edit a property text item.
        Returns True if the property text item was edited, False otherwise.
        """
        from .items.property_text import PropertyTextItem
        # check property existence
        if not self.has(name):
            logger().warning(f"Property '{name}' not found")
            return False
        # get property instance
        property = self._dict[name]
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
        if rotation  is not NO_CHANGE: pt.setRotation(rotation)
        if flip      is not NO_CHANGE: pt.setFlip(flip)
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

    def delText(self : Self, name : str) -> bool:
        """
        Delete a property text item.
        Returns True if the property text item was deleted, False otherwise.
        """
        from .items.property_text import PropertyTextItem
        # check property existence
        if not self.has(name):
            logger().warning(f"Property '{name}' not found")
            return False
        # get property instance
        property = self._dict[name]
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


class PropertiesMixin:
    # class attributes
    _PROPERTIES     : dict[str, InherentProperty]
    _PROPERTY_TEXTS : dict[str, PropertyTextSpec]

    # instance attributes
    properties : PropertiesManager

    def initProperties(self : Self, fresh : bool) -> None:
        self.properties = PropertiesManager(self, fresh)

    def signalPropertyChanges(self : Self, names : str | list[str]) -> None:
        if hasattr(self, "properties"):
            self.properties.signalChanges(names)
