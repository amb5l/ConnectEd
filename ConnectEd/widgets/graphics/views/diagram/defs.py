from typing import Self
from enum import Enum, auto

from PyQt6.QtCore    import Qt, QPoint, QPointF

from .....core.defs import LAYERS_SHEET, LAYERS_DRAWING

from .....app import settings

from .....core.check import checked


class DiagramViewLayer(Enum):
    Sheet   = LAYERS_SHEET
    Drawing = LAYERS_DRAWING


class DiagramViewGrid:
    display    : bool
    snap       : bool
    pitch      : QPointF
    dots       : bool
    alpha      : int
    min_pixels : int

    @checked
    def __init__(self : Self) -> None:
        s = settings().get("defaults/grid")
        self.display    = s.display
        self.snap       = s.snap
        self.pitch      = s.pitch
        self.dots       = s.dots
        self.alpha      = s.alpha
        self.min_pixels = s.min_pixels
