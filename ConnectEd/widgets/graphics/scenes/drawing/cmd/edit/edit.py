from typing import Self, Protocol
from dataclasses import dataclass

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QColor

from .....dialogs.properties import DisplayChoice, \
                                    PropertyVariables, PropertyChange

from ....properties import PropertiesMixin

from ....items import Default, NoChange, NO_CHANGE, SignalDirection

from ....items.mixin         import ItemMixin
from ....items.mixin.pos_rot import ItemPosRotMixin
from ....items.mixin.handle  import ItemHandlesMixin
from ....items.mixin.line    import ItemLineMixin
from ....items.mixin.fill    import ItemFillMixin
from ....items.mixin.quill   import ItemQuillMixin


from ....items.base_text import BaseTextLine, BaseTextBlock
from ....items.property_text import PropertyTextMixin, \
                                    PropertyTextLine, PropertyTextBlock

from . import CmdBase, CmdSceneItem, CmdSceneItems

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....scenes.drawing   import DrawingScene
    from ....items.port_pin   import PortPinMixin
    from ....items.symbol_pin import SymbolPin
















