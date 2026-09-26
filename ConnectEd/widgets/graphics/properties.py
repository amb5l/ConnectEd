from __future__ import annotations

import re

from typing          import Self, Any, TypeVar, Generic
from collections.abc import Callable, Sequence
from dataclasses     import dataclass, field, fields

from PyQt6.QtCore    import QObject, pyqtSignal
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsScene

from ...app        import logger

from ...core.check import checked
from ...core.types import NoChange, NO_CHANGE, DataKind
from ...core.utils import val2str, pascal2proper

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .items.property_text import (
        PropertyTextItem,
        PropertyTextSpec, PropertyTextState, PropertyTextPending,
        PropertyTextEdit
    )


class PropertyNotifier(QObject):
    changed = pyqtSignal()


class Property:
    """Object representing a property of a properties mixin."""

    _owner        : PropertiesMixin
    _kind         : DataKind                               | Callable[[PropertiesMixin], DataKind]
    _value        : Any                                    | None
    _getter       : Callable[[PropertiesMixin], Any]       | None
    _setter       : Callable[[PropertiesMixin, Any], None] | None
    _default      : Callable[[PropertiesMixin], Any]       | None
    _worthy       : Callable[[PropertiesMixin], bool]      | None
    _notifier     : PropertyNotifier                       | None
    _tip          : str                                    | None

    def __init__(
        self    : Self,
        owner   : PropertiesMixin,
        kind    : DataKind                               | Callable[[PropertiesMixin], DataKind],
        value   : Any                                    | None = None,
        getter  : Callable[[PropertiesMixin], Any]       | None = None,
        setter  : Callable[[PropertiesMixin, Any], None] | None = None,
        default : Callable[[PropertiesMixin], Any]       | None = None,
        worthy  : Callable[[PropertiesMixin], bool]      | None = None,
        tip     : str                                    | None = None
    ) -> None:
        self._owner        = owner
        self._kind         = kind
        self._value        = value
        self._getter       = getter
        self._setter       = setter
        self._default      = default
        self._worthy       = worthy
        self._notifier     = None
        self._tip          = tip

    def owner(self : Self) -> PropertiesMixin:
        return self._owner

    def isInherent(self : Self) -> bool:
        return self._getter is not None

    def isCustom(self : Self) -> bool:
        return not self.isInherent()

    def writeable(self : Self) -> bool:
        return self._setter is not None

    def name(self : Self) -> str:
        name = self._owner.propertyName(self)
        if name is None:
            raise ValueError("Property not found")
        return name

    def kind(self : Self) -> DataKind:
        return self._kind(self._owner) if callable(self._kind) \
            else self._kind

    def setKind(
        self : Self,
        kind : DataKind | Callable[[PropertiesMixin], DataKind]
    ) -> None:
        if self.isCustom() and kind not in (DataKind.STR, DataKind.TEXT):
            raise ValueError("Custom property kind must be STR or TEXT")
        self._kind = kind

    def value(
        self  : Self,
        slot  : Callable     | None = None,
        trail : list[object] | None = None,
        raw   : bool = False
    ) -> Any:
        trail = trail or []
        # detect recursion issues
        name = self.name()
        if self in trail:
            logger().warning(
                f"Property '{name}' substitution recursion loop: {trail}"
            )
            return None
        trail = trail + [self]
        if len(trail) > 10:
            logger().warning(
                f"Property '{name}' substitution recursion depth exceeded: {trail}"
            )
            return None
        # if slot is specified, connect the notifier to it
        if slot:
            # ensure that a notifier exists
            self._notifier = self._notifier or PropertyNotifier()
            # avoid duplicate connections
            try:
                self._notifier.changed.disconnect(slot)
            except TypeError:
                pass
            self._notifier.changed.connect(slot)
        # get value
        if self.isInherent():
            # inherent (no substitution)
            if not callable(self._getter):
                raise ValueError("Inherent property has no getter")
            return self._getter(self._owner)
        elif raw:
            return self._value
        else:
            # custom with substitution
            def repl(match: re.Match) -> str:
                var_name = match.group(1)
                # look locally, then (for items) in the scene
                if var_name in self._owner.properties:
                    property = self._owner.properties[var_name]
                    return str(property.value(slot, trail))
                elif isinstance(self._owner, QGraphicsItem):
                    scene = self._owner.scene()
                    if isinstance(scene, PropertiesMixin):
                        if var_name in scene.properties:
                            property = scene.properties[var_name]
                            return str(property.value(slot, trail))
                return f"<{var_name}>"  # unresolved substitution
            return re.sub(r'\{(\w+)\}', repl, val2str(self._value))

    def setValue(self : Self, value : Any) -> None:
        if callable(self._setter):
            self._setter(self._owner, value)
        else:
            self._value = value
        self.notify()

    def default(self : Self) -> Any:
        if callable(self._default):
            return self._default(self._owner)
        return None

    def worthy(self : Self) -> bool:
        return self._worthy is None or \
            (callable(self._worthy) and self._worthy(self._owner))

    def notify(self : Self) -> None:
        if self._notifier and self._owner.propertiesLive():
            self._notifier.changed.emit()

    def subscribe(self : Self, slot : Callable) -> None:
        if self._notifier is None:
            self._notifier = PropertyNotifier()
        self._notifier.changed.connect(slot)

    def unsubscribe(self : Self, slot : Callable) -> None:
        if self._notifier:
            try:
                self._notifier.changed.disconnect(slot)
            except TypeError:
                pass

    def state(self : Self) -> PropertyState:
        return PropertyState(
            name=self.name(),
            value=self.value(raw=True),
            kind=self.kind()
        )

    @classmethod
    def fromSpec(
        cls   : type[Self],
        owner : PropertiesMixin,
        spec  : PropertySpec
    ) -> Self:

        return cls(
            owner   = owner,
            kind    = spec.kind,
            value   = spec.value,
            getter  = spec.getter,
            setter  = spec.setter,
            default = spec.default,
            worthy  = spec.worthy,
            tip     = spec.tip
        )


T = TypeVar("T")

@dataclass
class PropertySpec(Generic[T]):
    """Used to create a property in owner definitions."""

    kind    : DataKind                           | Callable[[T], DataKind]
    value   : Any                                | None = None
    getter  : Callable[[T], Any]                 | None = None
    setter  : Callable[[T, Any], None]           | None = None
    default : Callable[[T], Any]                 | None = None
    worthy  : Callable[[T], bool]                | None = None
    tip     : str                                | None = None


@dataclass
class PropertyState:
    """Used to capture property states in editor dialogs."""

    name  : str
    value : Any
    kind  : DataKind


@dataclass
class PropertyPending:
    """Working copy of a property inside an editor dialog."""

    obj   : Property      | None  # None if new
    state : PropertyState | None  # None if deleted
    texts : list[PropertyTextPending]

    @checked
    def __init__(
        self   : Self,
        source : Property | PropertyState
    ) -> None:
        if isinstance(source, Property):
            from .items.property_text import PropertyTextPending
            self.obj   = source
            self.state = source.state()
            self.texts = [
                PropertyTextPending(item)
                for item in source.owner().propertyTextItems(source)
            ]
        else:
            self.obj   = None
            self.state = source
            self.texts = []

    @checked
    def getEdit(
        self  : Self,
        owner : PropertiesMixin
    ) -> PropertyAndTextsEdit | None:
        """Return this pending's edits, or None when it produces none."""
        if self.state is None:
            if self.obj is None:
                return None
            return PropertyAndTextsEdit(owner, self.obj, PropertyDelete(), [])
        if self.obj is None:
            return PropertyAndTextsEdit(owner, None, PropertyAdd(self.state, [
                text.state
                for text in self.texts
                if text.state is not None
            ]), [])
        change = PropertyChange.fromComparison(self.obj.state(), self.state)
        edit = None if change.noop() else change
        texts = []
        for text in self.texts:
            if (text_edit := text.getEdit(owner, self.obj)) is not None:
                texts.append(text_edit)
        if edit is None and len(texts) == 0:
            return None
        return PropertyAndTextsEdit(owner, self.obj, edit, texts)


@dataclass
class PropertyEdit:
    """Base class for carrying a property edit."""

    pass


@dataclass
class PropertyAdd(PropertyEdit):
    """Property Edit: add a new property."""

    state : PropertyState
    texts : list[PropertyTextState] = field(default_factory=list)


@dataclass
class PropertyDelete(PropertyEdit):
    """Property Edit: delete an existing property."""

    pass


@dataclass
class PropertyChange(PropertyEdit):
    """Property Edit: change an existing property."""

    name  : str      | NoChange = NO_CHANGE
    value : Any      | NoChange = NO_CHANGE
    kind  : DataKind | NoChange = NO_CHANGE

    @classmethod
    def fromComparison(
        cls    : type[Self],
        before : PropertyState,
        after  : PropertyState
    ) -> Self:
        kwargs : dict[str, Any] = {}
        for state_field in fields(before):
            before_value = getattr(before, state_field.name)
            after_value  = getattr(after,  state_field.name)
            if before_value != after_value:
                kwargs[state_field.name] = after_value
        return cls(**kwargs)

    def noop(self : Self) -> bool:
        """Return True if the edit is a no-op."""
        return all(
            isinstance(getattr(self, state_field.name), NoChange)
            for state_field in fields(PropertyState)
        )


@dataclass
class PropertyAndTextsEdit:
    """A property edit and the text edits that belong with it."""

    owner    : PropertiesMixin
    property : Property                                      | None
    edit     : PropertyAdd | PropertyDelete | PropertyChange | None
    texts    : Sequence[PropertyTextEdit]


class PropertiesMixin:
    _PROPERTIES     : dict[str, PropertySpec]
    _PROPERTY_TEXTS : dict[str, PropertyTextSpec]
    properties      : dict[str, Property]

    def initProperties(self : Self, live : bool) -> None:
        self.properties = {}
        self._live = live
        for name, spec in self._PROPERTIES.items():
            self.properties[name] = Property.fromSpec(self, spec)
        if live and hasattr(self, "_PROPERTY_TEXTS"):
            for name, spec in self._PROPERTY_TEXTS.items():
                if name not in self.properties:
                    logger().error(f"Property {name} does not exist")
                    continue
                text = self.propertyTextAdd(self.properties[name])
                text.apply(spec)

    def propertiesLive(self : Self) -> bool:
        return self._live

    @checked
    def setPropertiesLive(self : Self, live : bool) -> None:
        self._live = live

    @checked
    def propertyInit(
        self  : Self,
        name  : str,
        kind  : DataKind,
        value : Any
    ) -> Property | None:
        """
        Initialize a property. Creates if required, and sets the value;
        for use in deserialization.
        """
        if name in self.properties:
            property = self.properties[name]
            property.setKind(kind)
            property.setValue(value)
        else:
            property = self.propertyAdd(name, kind, value)
        return property

    @checked
    def propertyAdd(
        self  : Self,
        name  : str,
        kind  : DataKind,
        value : Any
    ) -> Property | None:
        """
        Add a property.
        Returns True if the property was added, False otherwise.
        """
        # check for existing property
        if name in self.properties:
            logger().error(f"Property '{name}' already exists")
            return None
        # check kind
        if kind not in (DataKind.STR, DataKind.TEXT):
            logger().error(f"Invalid property kind: {kind}")
            return None
        # create custom property
        property = Property(self, kind, value)
        self.properties[name] = property
        return property

    @checked
    def propertyRename(self : Self, old_name : str, new_name : str) -> bool:
        """
        Rename a property.
        Returns True if the property was renamed, False otherwise.
        """
        # check for existing property
        if old_name not in self.properties:
            logger().error(f"Property '{old_name}' not found")
            return False
        # check for no change
        if old_name == new_name:
            logger().warning(f"Old and new names are the same: {old_name}")
            return False
        # check for clash with existing property
        if new_name in self.properties:
            logger().error(f"Property '{new_name}' already exists")
            return False
        # get property instance
        property = self.properties[old_name]
        # check if inherent
        if property.isInherent():
            logger().error(f"Cannot rename inherent property '{old_name}'")
            return False
        # rename
        self.properties[new_name] = property
        del self.properties[old_name]
        # notify subscribers
        property.notify()
        # rename substitutions
        pattern = r'(?<!\\)\{' + re.escape(old_name) + r'\}'
        repl = '{' + new_name + '}'
        for other_name, other_property in self.properties.items():
            if other_name == new_name or other_property.isInherent():
                continue
            raw = other_property.value(raw = True)
            if not isinstance(raw, str):
                logger().error(f"Property '{other_name}' has non-string value")
                continue
            if re.search(pattern, raw) is None:
                continue
            other_property.setValue(re.sub(pattern, repl, raw))
        return True

    @checked
    def propertyDelete(self : Self, name : str) -> bool:
        """
        Remove a property and its texts.
        Returns True if the property was removed, False otherwise.
        """
        # check property existence
        if name not in self.properties:
            logger().error(f"Property '{name}' not found")
            return False
        # get property instance
        property = self.properties[name]
        # check if inherent
        if property.isInherent():
            logger().error(f"Inherent property '{name}' cannot be removed")
            return False
        for text in self.propertyTextItems(property):
            self.propertyTextRemove(text)
        # notify property receivers
        property.notify()
        # remove property from dictionary
        del self.properties[name]
        # done
        return True

    @checked
    def propertyName(self : Self, property : Property) -> str | None:
        return next(
            (n for n, p in self.properties.items() if p == property),
            None
        )

    def propertyTextAdd(self : Self, property : Property) -> PropertyTextItem:
        from .items.property_text import PropertyTextItem
        text = PropertyTextItem(property = property)
        if isinstance(self, QGraphicsScene):
            self.addItem(text)
        return text

    def propertyTextRemove(self : Self, text : PropertyTextItem) -> None:
        text.property().unsubscribe(text.onTextChanged)
        if isinstance(self, QGraphicsItem):
            text.setParentItem(None)
            if (scene := text.scene()) is not None:
                scene.removeItem(text)
        elif isinstance(self, QGraphicsScene):
            self.removeItem(text)
        else:
            raise ValueError("Owner is not a scene or item")

    def propertyTextAttach(self : Self, text : PropertyTextItem) -> None:
        text.property().subscribe(text.onTextChanged)
        if isinstance(self, QGraphicsScene):
            self.addItem(text)
        elif isinstance(self, QGraphicsItem):
            text.setCleat(text.cleat())
        else:
            raise ValueError("Owner is not a scene or item")

    def propertyTextItems(
        self     : Self,
        property : Property | None = None
    ) -> list[PropertyTextItem]:
        from .items.property_text import PropertyTextItem
        if isinstance(self, QGraphicsScene):
            items = [
                item
                for item in self.items()
                if isinstance(item, PropertyTextItem)
            ]
        elif isinstance(self, QGraphicsItem):
            items = []
            for child in self.childItems():
                if isinstance(child, PropertyTextItem):
                    items.append(child)
                for grandchild in child.childItems():
                    if isinstance(grandchild, PropertyTextItem):
                        items.append(grandchild)
        else:
            return []
        if property is not None:
            return [item for item in items if item.property() is property]
        return items

    def description(self : Self) -> str:
        class_name = self.__class__.__name__
        if class_name.endswith("Item"):
            class_name = class_name[:-4]
        elif class_name.endswith("Scene"):
            class_name = class_name[:-5]
        return pascal2proper(class_name)
