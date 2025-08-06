from typing import Self

from PyQt6.QtCore import QPointF

from pyTooling.Decorators import export

from ...items import EdgeLoc,      \
                     ElementMixin, \
                     Port,         \
                     PinRect,      \
                     Block,        \
                     BlockPin,     \
                     Rectangle,    \
                     Text,         \
                     TextBlock

from .cmd import cmdBase, cmdSceneBase


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene

