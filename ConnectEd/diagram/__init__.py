from dataclasses import dataclass, field
from types import SimpleNamespace
from PyQt6.QtCore import QSizeF

from settings import prefs

from .paint import DiagramPaintMixin
from .slots.file import DiagramSlotsFileMixin
from .slots.help import DiagramSlotsHelpMixin
from .misc import DiagramMiscMixin


'''
The Diagram class encapsulates the data and methods for a diagram.
'''
class Diagram(
    DiagramPaintMixin,
    DiagramSlotsFileMixin,
    DiagramSlotsHelpMixin,
    DiagramMiscMixin
):
    @dataclass
    class DiagramData:
        modified : bool   = False
        title    : str    = None
        size     : QSizeF = field(default_factory=QSizeF)
        margin   : float  = None
        content  : list   = field(default_factory=list)
        wip      : list   = field(default_factory=list)

    def __init__(self):
        self.window = None
        self.data = None
        self.slots = SimpleNamespace()
        self.selected = []
        self.extents = QSizeF(0.0,0.0)

    def setWindow(self, window):
        self.window = window

    def new(self, title, size = None, margin = None):
        self.data = self.DiagramData()
        self.data.modified = True
        self.data.title    = title
        self.data.size     = prefs.file.new.size if size is None else size
        self.data.margin   = prefs.file.new.margin if margin is None else margin
        self.data.content  = []
        self.data.wip      = []

        self.selected = []
        self.extents = self.data.size # empty diagram extents = sheet size
        # diagram now exists so enable all relevant slots

    # decorator for slot functions
    def slot(self, func):
        setattr(self.slots, func.__name__, func)
        return func

