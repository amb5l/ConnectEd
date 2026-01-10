from typing          import Self, Any, TypeAlias
from collections.abc import Callable
from dataclasses     import dataclass

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui  import QColor

from ...app import logger

from ...core.utils import str2val

from .items import Default, NoChange, NO_CHANGE, AlignH, AlignV

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .scenes.drawing import DrawingScene
    from .items import ItemType
    from .items.property_text import PropertyTextSpec, \
                                     PropertyTextLine, PropertyTextBlock
    PropertyOwner = ItemType | DrawingScene


@dataclass
class PropertySpec:
    kind    : str                                            = "str"
    valid   : Callable[["PropertyOwner"], bool]      | None  = None  # for XML
    getter  : Callable[["PropertyOwner"], Any] | str | None  = None
    setter  : Callable[["PropertyOwner", Any], None] | None  = None
    default : Callable[["PropertyOwner"], Any]       | None  = None
    text    : "PropertyTextSpec                      | None" = None


@dataclass
class PropertyTextLineState:
    hidden    : bool
    cleat     : str
    offset_x  : float
    offset_y  : float
    origin    : str
    color     : QColor | Default
    font      : str    | Default
    size      : float  | Default
    bold      : bool   | Default
    italic    : bool   | Default
    underline : bool   | Default


@dataclass
class PropertyTextLineEdit:
    hidden    : bool             | NoChange = NO_CHANGE
    cleat     : str              | NoChange = NO_CHANGE
    offset_x  : float            | NoChange = NO_CHANGE
    offset_y  : float            | NoChange = NO_CHANGE
    origin    : str              | NoChange = NO_CHANGE
    color     : QColor | Default | NoChange = NO_CHANGE
    font      : str    | Default | NoChange = NO_CHANGE
    size      : float  | Default | NoChange = NO_CHANGE
    bold      : bool   | Default | NoChange = NO_CHANGE
    italic    : bool   | Default | NoChange = NO_CHANGE
    underline : bool   | Default | NoChange = NO_CHANGE


@dataclass
class PropertyTextBlockState(PropertyTextLineState):
    align_h : AlignH
    align_v : AlignV
    width   : float | None
    height  : float | None


@dataclass
class PropertyTextBlockEdit(PropertyTextLineEdit):
    align_h : AlignH       | NoChange = NO_CHANGE
    align_v : AlignV       | NoChange = NO_CHANGE
    width   : float | None | NoChange = NO_CHANGE
    height  : float | None | NoChange = NO_CHANGE


PropertyTextEdit : TypeAlias = (
    NoChange               | # no change
    PropertyTextLineEdit   | # edit existing line
    PropertyTextBlockEdit  | # edit existing block
    PropertyTextLineState  | # convert existing block to line
    PropertyTextBlockState | # convert existing line to block
    PropertyTextLineState  | # add new line
    PropertyTextBlockState | # add new block
    None                     # remove property text
)


@dataclass
class PropertyState:
    name    : str
    value   : Any
    display : None | PropertyTextLineState | PropertyTextBlockState


@dataclass
class PropertyEdit:
    name    : str | NoChange
    value   : Any | NoChange
    display : PropertyTextEdit


class Property(QObject):
    # instance attributes
    _owner    : "PropertyOwner"
    _name     : str
    _kind     : str
    _valid    : Callable[["PropertyOwner"], bool]      | None
    _getter   : Callable[["PropertyOwner"], Any] | str | None  # or static value
    _setter   : Callable[["PropertyOwner", Any], None] | None
    _default  : Callable[["PropertyOwner"], Any]       | None
    _text     : "PropertyTextLine | PropertyTextBlock | None"
    _inherent : bool
    _subs     : dict["Property", Callable]  # dep_property -> update_slot

    # signals
    changed = pyqtSignal(object)

    def __init__(
        self     : Self,
        owner    : "PropertyOwner",
        name     : str,
        kind     : str,
        valid    : Callable[["PropertyOwner"], bool]      | None  = None,
        getter   : Callable[["PropertyOwner"], Any] | str | None  = None,
        setter   : Callable[["PropertyOwner", Any], None] | None  = None,
        default  : Callable[["PropertyOwner"], Any]       | None  = None,
        text     : "PropertyTextLine | PropertyTextBlock  | None" = None,
        inherent : bool = False
    ) -> None:
        super().__init__()
        self._owner    = owner
        self._name     = name
        self._kind     = kind
        self._valid    = valid
        self._getter   = getter
        self._setter   = setter
        self._default  = default
        self._text     = text
        self._inherent = inherent
        self._subs     = {}

    def name(self : Self) -> str:
        return self._name

    def inherent(self : Self) -> bool:
        return self._inherent

    def isReadOnly(self : Self) -> bool:
        return self._setter is None and not isinstance(self._getter, str)

    def kind(self : Self) -> str:
        return self._kind

    def valid(self : Self) -> bool:
        """Check if this property is valid for the given owner (e.g., for XML)."""
        return self._valid(self._owner) if self._valid else True

    def raw(self : Self) -> Any:
        """Get raw value without substitution."""
        if isinstance(self._getter, str):
            return self._getter
        elif self._getter and callable(self._getter):
            return self._getter(self._owner)
        else:
            return None

    def get(self : Self, recurse: int = 0, subscribe : bool = True) -> Any:
        """Get value, applying substitution and subscriptions if needed."""
        if recurse > 10:  # prevent infinite recursion
            logger().warning(
                f"Property '{self._name}' recursion depth exceeded"
            )
            return f"{{RECURSION_ERROR:{self._name}}}"
        raw_value = self.raw()
        if isinstance(raw_value, str):
            return self._substituteAndSubscribe(
                raw_value, recurse + 1, subscribe
            )
        return raw_value

    def set(self : Self, value : Any) -> None:
        """Set value and notify subscribers."""
        old_value = self.get(subscribe=False)  # Don't resubscribe during get
        if self._setter:
            if isinstance(value, str) and self._kind != "str":
                value = str2val(value, self._kind)
            self._setter(self._owner, value)
        elif isinstance(self._getter, str) or self._getter is None:
            self._getter = value
        else:
            logger().error(f"Property '{self._name}' has no setter")
            return
        # Clear subscriptions if new value doesn't need them
        if not isinstance(value, str) and self._text is not None:
            self._clearSubs()
        if old_value != value:
            self.changed.emit(value)  # Propagate change

    def default(self : Self) -> Any:
        """Get default value."""
        return self._default(self._owner) if self._default else None

    def getText(self : Self) -> "PropertyTextLine | PropertyTextBlock | None":
        return self._text

    def setText(
        self : Self,
        text : "PropertyTextLine | PropertyTextBlock | None"
    ) -> None:
        # Disconnect from old property text if exists
        if self._text is not None:
            try:
                self.changed.disconnect(self._text.onPropertyChange)
            except TypeError:
                pass
        # If removing property text, delete it from scene
        if text is None and self._text is not None:
            scene = self._text.scene()
            if scene is not None:
                scene.removeItem(self._text)
        self._text = text
        # Connect to new property text if provided
        if text is not None:
            self.changed.connect(text.onPropertyChange)

    def getState(self : Self) -> "PropertyState":
        pt_state_class = None
        if isinstance(self._text, PropertyTextLine):
            pt_state_class = PropertyTextLineState
        elif isinstance(self._text, PropertyTextBlock):
            pt_state_class = PropertyTextBlockState
        args = {}
        if pt_state_class is not None:
            args[ "hidden"    ] = not self._text.isVisible(),
            args[ "cleat"     ] = self._text.getCleat(),
            args[ "offset_x"  ] = self._text.pos().x(),
            args[ "offset_y"  ] = self._text.pos().y(),
            args[ "origin"    ] = self._text.getOrigin(),
            args[ "color"     ] = self._text.quillColor(),
            args[ "font"      ] = self._text.quillFamily(),
            args[ "size"      ] = self._text.quillSize(),
            args[ "bold"      ] = self._text.quillBold(),
            args[ "italic"    ] = self._text.quillItalic(),
            args[ "underline" ] = self._text.quillUnderline()
        if pt_state_class == PropertyTextBlockState:
            args["align_h"    ] = self._text.alignH()
            args["align_v"    ] = self._text.alignV()
            args["width"      ] = self._text.width()
            args["height"     ] = self._text.height()
        pt_state = pt_state_class(**args) if args else None
        return PropertyState(self.name(), self.raw(), pt_state)

    def clone(self : Self, new_owner : "PropertyOwner") -> "Property":
        """Create a clone of this property with a new owner."""
        clone = Property(
            new_owner,
            self._name,
            self._kind,
            self._valid,
            self._getter,
            self._setter,
            self._default
        )
        clone.set(self.get())
        return clone

    def _substituteAndSubscribe(
        self      : Self,
        value     : str,
        recurse   : int,
        subscribe : bool
    ) -> str:
        """Parse {var_name}, resolve, and subscribe to changes."""
        import re
        # Clear old subscriptions when subscribing (each property manages its own)
        if subscribe and self._subs:
            self._clearSubs()
        # Replace {var_name} with the value of the dependent property,
        # subscribing to changes.
        def repl(match: re.Match) -> str:
            var_name = match.group(1)
            prop_dep = None
            # Look for local property first
            if hasattr(self._owner, 'properties') \
            and var_name in self._owner.properties:
                prop_dep = self._owner.properties[var_name]
                # Nested deps subscribe independently
                result = str(prop_dep.get(recurse, subscribe=subscribe))
            # Fallback to scene
            else:
                scene = self._owner.scene() if hasattr(self._owner, 'scene') \
                    else self._owner  # For scene itself, _owner is scene
                if hasattr(scene, 'properties') \
                and var_name in scene.properties:
                    prop_dep = scene.properties[var_name]
                    result = str(prop_dep.get(recurse, subscribe=subscribe))
                else:
                    return match.group(0)  # Unresolved: leave as-is
            # Subscribe to this property's direct dependencies (once per property)
            if subscribe and prop_dep not in self._subs:
                # Create slot that updates text display and propagates signal
                def update_slot(_value=None):
                    # Update text display if present
                    if self._text is not None:
                        self._text.onPropertyChange()
                    # Propagate change signal for chained dependencies
                    self.changed.emit(self.get(subscribe=False))
                prop_dep.changed.connect(update_slot)
                self._subs[prop_dep] = update_slot
            return result
        return re.sub(r'\{(\w+)\}', repl, value)

    def _clearSubs(self : Self) -> None:
        """Clear all subscriptions."""
        for prop, slot in self._subs.items():
            try:
                prop.changed.disconnect(slot)
            except TypeError:
                pass
        self._subs.clear()
