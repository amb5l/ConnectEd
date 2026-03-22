from typing      import Any, TypeAlias
from dataclasses import dataclass

from ....core.types import NoChange, NO_CHANGE, AlignH, AlignV, \
                           HandleId, RectHandleId, DataKind, QColor


@dataclass
class PropertyChangeBase:
    name : str

@dataclass
class PropertyChangeAddModify(PropertyChangeBase):
    kind  : DataKind | NoChange = NO_CHANGE
    value : Any      | NoChange = NO_CHANGE


@dataclass
class PropertyChangeAdd(PropertyChangeAddModify):
    pass


@dataclass
class PropertyChangeModify(PropertyChangeAddModify):
    pass


@dataclass
class PropertyChangeDelete(PropertyChangeBase):
    pass


@dataclass
class PropertyChangeTextAddModify(PropertyChangeBase):
    visible   : bool         | NoChange = NO_CHANGE
    cleat     : HandleId     | NoChange = NO_CHANGE
    x         : float        | NoChange = NO_CHANGE
    y         : float        | NoChange = NO_CHANGE
    rotation  : float        | NoChange = NO_CHANGE
    flip      : bool         | NoChange = NO_CHANGE
    origin    : RectHandleId | NoChange = NO_CHANGE
    align_h   : AlignH       | NoChange = NO_CHANGE
    align_v   : AlignV       | NoChange = NO_CHANGE
    width     : float        | NoChange = NO_CHANGE
    height    : float        | NoChange = NO_CHANGE
    color     : QColor       | NoChange = NO_CHANGE
    family    : str          | NoChange = NO_CHANGE
    size      : float        | NoChange = NO_CHANGE
    bold      : bool         | NoChange = NO_CHANGE
    italic    : bool         | NoChange = NO_CHANGE
    underline : bool         | NoChange = NO_CHANGE


@dataclass
class PropertyChangeTextAdd(PropertyChangeTextAddModify):
    pass


@dataclass
class PropertyChangeTextModify(PropertyChangeTextAddModify):
    pass


@dataclass
class PropertyChangeTextDelete(PropertyChangeBase):
    pass


PropertyChangeType : TypeAlias = (
    PropertyChangeDelete     |
    PropertyChangeAdd        |
    PropertyChangeModify     |
    PropertyChangeTextDelete |
    PropertyChangeTextAdd    |
    PropertyChangeTextModify
)
