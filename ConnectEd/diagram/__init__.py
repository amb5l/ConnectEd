from dataclasses import dataclass, field
from types import SimpleNamespace
from PyQt6.QtCore import QSizeF

from settings import prefs

from .events.paint import DiagramEventsPaintMixin
from .api.file import DiagramApiFileMixin
from .api.edit import DiagramApiEditMixin
from .misc import DiagramMiscMixin


class Diagram(
    DiagramEventsPaintMixin,
    DiagramApiFileMixin,
    DiagramApiEditMixin,
    DiagramMiscMixin
):
    @dataclass
    class DiagramData:
        path     : str    = None
        modified : bool   = False
        title    : str    = None
        size     : QSizeF = field(default_factory=QSizeF)
        margin   : float  = None
        content  : list   = field(default_factory=list)
        wip      : list   = field(default_factory=list)

    def __init__(self, title=None):
        if title is not None:
            self.data.modified = True
            self.data.title    = title
            self.data.size     = prefs.file.new.size
            self.data.margin   = prefs.file.new.margin
            self.data.content  = []
            self.data.wip      = []
        else:
            self.data = None

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
