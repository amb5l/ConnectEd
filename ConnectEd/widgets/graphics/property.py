from typing          import Self, Any
from collections.abc import Callable
from dataclasses     import dataclass

from PyQt6.QtCore import QObject, pyqtSignal

from ...app import logger

from ...core.utils import str2val

from .items import ItemType


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .scenes.drawing import DrawingScene
    PropertyOwner = ItemType | DrawingScene


@dataclass
class PropertySpec:
    type_name : str                                           = "str"
    getter    : Callable[["PropertyOwner"], Any] | str | None = None
    setter    : Callable[["PropertyOwner", Any], None] | None = None


class Property(QObject):
    # instance attributes
    _owner     : "PropertyOwner"
    _name      : str
    _type_name : str
    _getter    : Callable[["PropertyOwner"], Any] | str | None  # or static value
    _setter    : Callable[["PropertyOwner", Any], None] | None

    # signals
    changed = pyqtSignal(object)

    def __init__(
        self      : Self,
        owner     : "PropertyOwner",
        name      : str,
        type_name : str,
        getter    : Callable[["PropertyOwner"], Any] | str | None = None,
        setter    : Callable[["PropertyOwner", Any], None] | None = None
    ) -> None:
        super().__init__()
        self._owner     = owner
        self._name      = name
        self._type_name = type_name
        self._getter    = getter
        self._setter    = setter

    def typeName(self: Self) -> str:
        return self._type_name

    def get(self: Self) -> Any:
        """Get value, applying substitution if needed."""
        raw_value = \
            self._getter if isinstance(self._getter, str) else \
            self._getter(self._owner) if self._getter and callable(self._getter) else \
            None
        if isinstance(raw_value, str):
            return self._substitute(raw_value)
        return raw_value

    def set(self: Self, new_value: Any) -> None:
        """Set value and notify subscribers."""
        old_value = self.get()
        if self._setter:
            if isinstance(new_value, str) and self._type_name != "str":
                new_value = str2val(new_value, self._type_name)
            self._setter(self._owner, new_value)
        elif isinstance(self._getter, str) or self._getter is None:
            self._getter = new_value
        else:
            logger().error(f"Property '{self._name}' has no setter")
            return
        if old_value != new_value:
            self.changed.emit(new_value)  # Propagate change

    def isStatic(self: Self) -> bool:
        return not isinstance(self._getter, Callable)

    def isReadOnly(self: Self) -> bool:
        return not self._setter

    def _substitute(self: Self, value: str) -> str:
        """Parse {var_name} and resolve from local owner or scene."""
        import re
        def repl(match: re.Match) -> str:
            var_name = match.group(1)
            # Local item first
            if hasattr(self._owner, 'properties') \
            and var_name in self._owner.properties:
                return str(self._owner.properties[var_name].get())
            # Fallback to parent scene
            scene = self._owner.scene() if hasattr(self._owner, 'scene') \
                else self._owner  # For scene itself, _owner is scene
            if hasattr(scene, 'properties') and var_name in scene.properties:
                return str(scene.properties[var_name].get())
            return match.group(0)  # Unresolved: leave as-is
        return re.sub(r'\{(\w+)\}', repl, value)
