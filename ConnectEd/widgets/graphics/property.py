from typing          import Self, Any
from collections.abc import Callable
from dataclasses     import dataclass

from PyQt6.QtCore import QObject, pyqtSignal

from ...app import logger

from ...core.utils import str2val

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .scenes.drawing import DrawingScene
    from .items import ItemType
    from .items.property_text import PropertyTextSpec, PropertyTextMixin
    PropertyOwner = ItemType | DrawingScene


@dataclass
class PropertySpec:
    kind    : str                                            = "str"
    getter  : Callable[["PropertyOwner"], Any] | str | None  = None
    setter  : Callable[["PropertyOwner", Any], None] | None  = None
    valid   : Callable[["PropertyOwner"], bool]      | None  = None
    default : Callable[["PropertyOwner"], Any]       | None  = None
    text    : "PropertyTextSpec                      | None" = None


class Property(QObject):
    # instance attributes
    _owner   : "PropertyOwner"
    _name    : str
    _kind    : str
    _getter  : Callable[["PropertyOwner"], Any] | str | None  # or static value
    _setter  : Callable[["PropertyOwner", Any], None] | None
    _valid   : Callable[["PropertyOwner"], bool]      | None
    _default : Callable[["PropertyOwner"], Any]       | None
    _text    : "PropertyTextMixin | None"
    _subs    : dict["Property", Callable]  # dep_property -> update_slot

    # signals
    changed = pyqtSignal(object)

    def __init__(
        self    : Self,
        owner   : "PropertyOwner",
        name    : str,
        kind    : str,
        getter  : Callable[["PropertyOwner"], Any] | str | None = None,
        setter  : Callable[["PropertyOwner", Any], None] | None = None,
        valid   : Callable[["PropertyOwner"], bool] | None = None,
        default : Callable[["PropertyOwner"], Any] | None = None,
        text    : "PropertyTextMixin | None" = None
    ) -> None:
        super().__init__()
        self._owner   = owner
        self._name    = name
        self._kind    = kind
        self._getter  = getter
        self._setter  = setter
        self._valid   = valid
        self._default = default
        self._text    = text
        self._subs    = {}

    def isStatic(self: Self) -> bool:
        return not isinstance(self._getter, Callable)

    def isReadOnly(self: Self) -> bool:
        return self._setter is None and not isinstance(self._getter, str)

    def kind(self: Self) -> str:
        return self._kind

    def raw(self: Self) -> Any:
        """Get raw value without substitution."""
        if isinstance(self._getter, str):
            return self._getter
        elif self._getter and callable(self._getter):
            return self._getter(self._owner)
        else:
            return None

    def get(self: Self, recurse: int = 0, subscribe: bool = True) -> Any:
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

    def set(self: Self, new_value: Any) -> None:
        """Set value and notify subscribers."""
        old_value = self.get(subscribe=False)  # Don't resubscribe during get
        if self._setter:
            if isinstance(new_value, str) and self._kind != "str":
                new_value = str2val(new_value, self._kind)
            self._setter(self._owner, new_value)
        elif isinstance(self._getter, str) or self._getter is None:
            self._getter = new_value
        else:
            logger().error(f"Property '{self._name}' has no setter")
            return
        # Clear subscriptions if new value doesn't need them
        if not isinstance(new_value, str) and self._text is not None:
            self._clearSubs()
        if old_value != new_value:
            self.changed.emit(new_value)  # Propagate change

    def valid(self: Self) -> bool:
        """Check if this property is valid for the given owner (e.g., for XML)."""
        return self._valid(self._owner) if self._valid else True

    def default(self: Self) -> Any:
        """Get default value."""
        return self._default(self._owner) if self._default else None

    def getText(self : Self) -> "PropertyTextMixin | None":
        return self._text

    def setText(self : Self, text : "PropertyTextMixin | None") -> None:
        self._text = text

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
                        self._text.onTextChange()
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
