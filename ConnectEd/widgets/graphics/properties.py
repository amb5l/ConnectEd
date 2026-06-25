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

from ...core.check import checked

from ...core.types import NoChange, NO_CHANGE, AlignH, AlignV, \
                          HandleId, RectHandleId, DataKind
from ...core.utils import str2val, pascal2proper

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .scenes.drawing import DrawingScene
    from .items import ItemType
    from .items.property_text import PropertyTextSpec, PropertyTextItem
    Owner = ItemType | DrawingScene


@dataclass
class PropertyTextSpec:
    visible    : bool            = True
    cleat      : HandleId | None = None
    x          : float           = 0
    y          : float           = 0
    rotation   : float           = 0.0
    mirror_h   : bool            = False
    mirror_v   : bool            = False
    autoflip   : bool            = True
    origin     : RectHandleId    = RectHandleId.TOP_LEFT
    align_h    : AlignH          = AlignH.LEFT
    align_v    : AlignV          = AlignV.TOP
    width      : float           = -1.0
    height     : float           = -1.0
    pad_left   : float           = 0.0
    pad_right  : float           = 0.0
    pad_top    : float           = 0.0
    pad_bottom : float           = 0.0
    color      : QColor   | None = None
    font       : str      | None = None
    size       : float    | None = None
    bold       : bool     | None = None
    italic     : bool     | None = None
    underline  : bool     | None = None

    def astuple(self : Self) -> tuple:
        return (
            self.visible, self.cleat, self.x, self.y,
            self.rotation, self.mirror_h, self.mirror_v, self.autoflip,
            self.origin, self.align_h, self.align_v, self.width, self.height,
            self.pad_left, self.pad_right, self.pad_top, self.pad_bottom,
            self.color, self.font, self.size, self.bold, self.italic, self.underline
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
    tip      : str                                       | None = None


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
    _owner  : "PropertiesMixin"
    _dict   : dict[str, InherentProperty | CustomProperty]

    @checked
    def __init__(self : Self, owner : "PropertiesMixin", fresh : bool) -> None:
        """
        Initialize the properties system for this instance.
        """
        self._owner  = owner
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

    @checked
    def owner(self : Self) -> "PropertiesMixin":
        return self._owner

    @checked
    def names(self : Self) -> list[str]:
        return list(self._dict.keys())

    @checked
    def inherentNames(self : Self) -> list[str]:
        return [
            name for name, property in self._dict.items()
            if isinstance(property, InherentProperty)
        ]

    @checked
    def customNames(self : Self) -> list[str]:
        return [
            name for name, property in self._dict.items()
            if isinstance(property, CustomProperty)
        ]

    @checked
    def has(self : Self, name : str) -> bool:
        """
        Test property existance.
        Returns True if the property exists, False otherwise.
        """
        return name in self._dict

    @checked
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

    @checked
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

    @checked
    def kind(self : Self, name : str) -> DataKind | None:
        # check property existence
        if not self.has(name):
            logger().warning(f"Property '{name}' not found")
            return None
        # get property instance
        property = self._dict[name]
        # return kind
        if callable(property.kind):
            try:
                return property.kind(self._owner)
            except Exception:
                return None
        return property.kind

    @checked
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
        self.signalChanges(name)
        return True

    @checked
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

    @checked
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

    @checked
    def value(
        self   : Self,
        name   : str,
        slot   : Callable  | None = None,  # e.g. PropertyTextItem.onTextChanged
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

    @checked
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
        kind = self.kind(name)
        # inherent properties
        if isinstance(property, InherentProperty):
            if not callable(property.setter):
                logger().warning(f"Property '{name}' is read-only")
                return False
            # convert from str to appropriate type if necessary
            if isinstance(value, str) and kind is not None and kind != DataKind.STR:
                value = str2val(value, kind.types()[0].__name__)
            property.setter(self._owner, value)
            return True
        # custom properties
        elif isinstance(property, CustomProperty):
            if isinstance(value, kind.types()):
                property.value = value
            else:
                logger().warning(f"Bad property value type: {type(value)}")
                return False
            self.signalChanges(name)
            return True
        # unknown properties
        logger().warning(f"Bad property type: {type(property)}")
        return False

    @checked
    def init(self : Self, name : str, value : Any) -> bool:
        """
        Initialize a property. Creates if required, and sets the value;
        for use in deserialization, and for creating new custom properties.
        Returns True if the property was initialized, False otherwise.
        """
        if self.has(name):
            return self.setValue(name, value)
        if isinstance(value, bool):
            kind = DataKind.BOOL
        elif isinstance(value, int):
            kind = DataKind.INT
        elif isinstance(value, float):
            kind = DataKind.FLOAT
        else:
            kind = DataKind.STR
        return self.add(name, kind, value)

    @checked
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

    @checked
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
            logger().info(f"Old and new names are the same: {old_name}")
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
        if property.text is not None:
            property.text.bind(new_name)
        # notify subscribers
        self.signalChanges(new_name)
        # rename substitutions
        pattern = r'(?<!\\)\{' + re.escape(old_name) + r'\}'
        repl = '{' + new_name + '}'
        subst_changed : list[str] = []
        for name, prop in self._dict.items():
            if name == new_name or not isinstance(prop, CustomProperty):
                continue
            if prop.kind not in (DataKind.STR, DataKind.TEXT):
                continue
            if not isinstance(prop.value, str):
                logger().warning(f"Property '{name}' has non-string value")
                continue
            if old_name in prop.value:
                new_value = re.sub(pattern, repl, prop.value)
                prop.value = new_value
                subst_changed.append(name)
        # notify substitution subscribers
        if subst_changed:
            self.signalChanges(subst_changed)
        # done
        return True

    @checked
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
        # notify property receivers
        self.signalChanges(name)
        # remove property from dictionary
        del self._dict[name]
        # done
        return True

    @checked
    def signalChanges(self : Self, names : str | list[str]) -> None:
        if not self.owner().live():
            return
        if isinstance(names, str):
            names = [names]
        for name in names:
            if self.has(name):
                property = self._dict[name]
                if property.notifier:
                    property.notifier.changed.emit()

    @checked
    def syncInherentFrom(
        self  : Self,
        other : "PropertiesManager"
    ) -> None:
        for name in other.inherentNames():
            if self.has(name):
                if self.writeable(name):
                    self.setValue(name, other.value(name))
            else:
                logger().warning(f"Property '{name}' not found")

    @checked
    def syncCustomFrom(self : Self, other : "PropertiesManager") -> None:
        for name in self.customNames():
            if not other.has(name):
                self.delete(name)
            else:
                self.setValue(name, other.value(name))
        for name in other.customNames():
            if self.has(name):
                self.setValue(name, other.value(name))
            else:
                self.add(name, other.kind(name), other.value(name))

    @checked
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

    @checked
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
        text.onTextChanged()
        return True

    def texts(self : Self) -> list["PropertyTextItem"]:
        return [
            property.text
            for property in self._dict.values()
            if property.text is not None
        ]

    @checked
    def addText(
        self       : Self,
        name       : str,
        visible    : bool          = True,
        cleat      : HandleId      = RectHandleId.BOTTOM_LEFT,
        x          : float         = 0,
        y          : float         = 0,
        rotation   : float         = 0.0,
        mirror_h   : bool          = False,
        mirror_v   : bool          = False,
        autoflip   : bool          = True,
        origin     : RectHandleId  = RectHandleId.TOP_LEFT,
        align_h    : AlignH        = AlignH.LEFT,
        align_v    : AlignV        = AlignV.TOP,
        width      : float         = -1.0,
        height     : float         = -1.0,
        pad_left   : float         = 0.0,
        pad_right  : float         = 0.0,
        pad_top    : float         = 0.0,
        pad_bottom : float         = 0.0,
        color      : QColor | None = None,
        font       : str    | None = None,
        size       : float  | None = None,
        bold       : bool   | None = None,
        italic     : bool   | None = None,
        underline  : bool   | None = None
    ) -> bool:
        """
        Add a property text item. Replace any existing property text item.
        Returns True if the property text was added, False otherwise.
        """
        from .items.property_text import PropertyTextItem
        # check property existence
        if not self.has(name):
            logger().warning(f"Property '{name}' not found")
            return False
        # get property instance
        property = self._dict[name]
        # check for existing PropertyTextItem
        if property.text is not None:
            logger().warning(f"Property '{name}' already has text")
            return False
        # create new property text item
        property.text = PropertyTextItem(
            name       = name,
            cleat      = cleat,
            pos        = QPointF(x, y),
            rotation   = rotation,
            mirror_h   = mirror_h,
            mirror_v   = mirror_v,
            autoflip   = autoflip,
            origin     = origin,
            align_h    = align_h,
            align_v    = align_v,
            width      = width,
            height     = height,
            pad_left   = pad_left,
            pad_right  = pad_right,
            pad_top    = pad_top,
            pad_bottom = pad_bottom,
            color      = color,
            font       = font,
            size       = size,
            bold       = bold,
            italic     = italic,
            underline  = underline,
            parent     = self._owner
        )
        property.text.setVisible(visible)
        return True

    @checked
    def editText(
        self       : Self,
        name       : str,
        visible    : bool   | NoChange = NO_CHANGE,
        cleat      : str    | NoChange = NO_CHANGE,
        x          : float  | NoChange = NO_CHANGE,
        y          : float  | NoChange = NO_CHANGE,
        rotation   : float  | NoChange = NO_CHANGE,
        mirror_h   : bool   | NoChange = NO_CHANGE,
        mirror_v   : bool   | NoChange = NO_CHANGE,
        autoflip   : bool   | NoChange = NO_CHANGE,
        origin     : str    | NoChange = NO_CHANGE,
        align_h    : AlignH | NoChange = NO_CHANGE,
        align_v    : AlignV | NoChange = NO_CHANGE,
        width      : float  | NoChange = NO_CHANGE,
        height     : float  | NoChange = NO_CHANGE,
        pad_left   : float  | NoChange = NO_CHANGE,
        pad_right  : float  | NoChange = NO_CHANGE,
        pad_top    : float  | NoChange = NO_CHANGE,
        pad_bottom : float  | NoChange = NO_CHANGE,
        color      : QColor | NoChange = NO_CHANGE,
        font       : str    | NoChange = NO_CHANGE,
        size       : float  | NoChange = NO_CHANGE,
        bold       : bool   | NoChange = NO_CHANGE,
        italic     : bool   | NoChange = NO_CHANGE,
        underline  : bool   | NoChange = NO_CHANGE
    ) -> bool:
        """
        Edit a property text item.
        Returns True if the property text item was edited, False otherwise.
        """
        # check property existence
        if not self.has(name):
            logger().warning(f"Property '{name}' not found")
            return False
        # get property instance
        property = self._dict[name]
        # check PropertyTextItem existence
        if property.text is None:
            logger().warning(f"Property '{name}' does not have text")
            return False
        # get PropertyTextItem instance
        pt = property.text
        # edit PropertyTextItem
        if visible    is not NO_CHANGE: pt.setVisible(visible)
        if cleat      is not NO_CHANGE: pt.setCleat(cleat)
        if x          is not NO_CHANGE: pt.setX(x)
        if y          is not NO_CHANGE: pt.setY(y)
        if rotation   is not NO_CHANGE: pt.setRotation(rotation)
        if mirror_h   is not NO_CHANGE: pt.setMirrorH(mirror_h)
        if mirror_v   is not NO_CHANGE: pt.setMirrorV(mirror_v)
        if autoflip   is not NO_CHANGE: pt.setAutoflip(autoflip)
        if origin     is not NO_CHANGE: pt.setOrigin(origin)
        if align_h    is not NO_CHANGE: pt.setAlignH(align_h)
        if align_v    is not NO_CHANGE: pt.setAlignV(align_v)
        if width      is not NO_CHANGE: pt.setWidth(width)
        if height     is not NO_CHANGE: pt.setHeight(height)
        if pad_left   is not NO_CHANGE: pt.setPadLeft(pad_left)
        if pad_right  is not NO_CHANGE: pt.setPadRight(pad_right)
        if pad_top    is not NO_CHANGE: pt.setPadTop(pad_top)
        if pad_bottom is not NO_CHANGE: pt.setPadBottom(pad_bottom)
        if color      is not NO_CHANGE: pt.setTextColor(color)
        if font       is not NO_CHANGE: pt.setTextFont(font)
        if size       is not NO_CHANGE: pt.setTextSize(size)
        if bold       is not NO_CHANGE: pt.setTextBold(bold)
        if italic     is not NO_CHANGE: pt.setTextItalic(italic)
        if underline  is not NO_CHANGE: pt.setTextUnderline(underline)
        return True

    @checked
    def delText(self : Self, name : str) -> bool:
        """
        Delete a property text item.
        Returns True if the property text item was deleted, False otherwise.
        """
        # check property existence
        if not self.has(name):
            logger().warning(f"Property '{name}' not found")
            return False
        # get property instance
        property = self._dict[name]
        # check for existing PropertyTextItem
        if property.text is None:
            logger().warning(f"Property '{name}' does not have text")
            return False
        # disconnect notifier
        if property.notifier:
            try:
                property.notifier.changed.disconnect(
                    property.text.onTextChanged
                )
            except TypeError:
                pass
        # unparent PropertyTextItem
        property.text.setParentItem(None)
        # remove from scene
        property.text.scene().removeItem(property.text)
        # remove reference
        property.text = None
        return True

    @checked
    def addMissingTextsFrom(self : Self, other : "PropertiesManager") -> None:
        for pt in other.texts():
            if not self.has(pt.name()):
                logger().warning(f"Property '{pt.name()}' not found")
                continue
            if self.text(pt.name()) is not None:
                continue
            self.addText(*pt.propertyTuple())

    @checked
    def removeTextsNotIn(self : Self, other : "PropertiesManager") -> None:
        for pt in self.texts():
            if not other.has(pt.name()):
                logger().warning(f"Property '{pt.name()}' not found")
                continue
            if other.text(pt.name()) is None:
                self.delText(pt.name())

    @checked
    def syncTextFrom(self : Self, other : "PropertiesManager") -> None:
        for pt in self.texts():
            if not other.has(pt.name()):
                logger().warning(f"Property '{pt.name()}' not found")
            other_pt = other.text(pt.name())
            if other_pt is None:
                continue
            pt.setCleat(other_pt.cleat())
            pt.setPos(other_pt.pos())
            pt.setRotation(other_pt.rotation())
            pt.setMirrorH(other_pt.mirrorH())
            pt.setMirrorV(other_pt.mirrorV())
            pt.setAutoflip(other_pt.autoflip())
            pt.setOrigin(other_pt.origin())
            pt.setAlignH(other_pt.alignH())
            pt.setAlignV(other_pt.alignV())
            pt.setWidth(other_pt.width())
            pt.setHeight(other_pt.height())
            pt.setPadLeft(other_pt.padLeft())
            pt.setPadRight(other_pt.padRight())
            pt.setPadTop(other_pt.padTop())
            pt.setPadBottom(other_pt.padBottom())
            pt.setTextColor(other_pt.textColor())
            pt.setTextFont(other_pt.textFont())
            pt.setTextSize(other_pt.textSize())
            pt.setTextBold(other_pt.textBold())
            pt.setTextItalic(other_pt.textItalic())


class PropertiesMixin:
    # class attributes
    _PROPERTIES     : dict[str, InherentProperty]
    _PROPERTY_TEXTS : dict[str, PropertyTextSpec]

    # instance attributes
    properties : PropertiesManager
    _live      : bool               # not live = deserializing

    @checked
    def initProperties(self : Self, fresh : bool) -> None:
        self.properties = PropertiesManager(self, fresh)
        self._live = fresh

    @checked
    def description(self : Self) -> str:
        class_name = self.__class__.__name__
        class_name = class_name.removesuffix("Item")
        class_name = class_name.removesuffix("Scene")
        return pascal2proper(class_name)

    def live(self : Self) -> bool:
        return self._live

    def setLive(self : Self, live : bool) -> None:
        self._live = live
