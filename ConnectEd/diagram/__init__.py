from dataclasses import dataclass, field
from PyQt6.QtCore import QSizeF

from settings import settings

from .events.paint import DiagramEventsPaintMixin
from .api          import DiagramApiMixin
from .api.file     import DiagramApiFileMixin
from .api.edit     import DiagramApiEditMixin
from .misc         import DiagramMiscMixin


class Diagram(
    DiagramEventsPaintMixin,
    DiagramApiMixin,
    DiagramApiFileMixin,
    DiagramApiEditMixin,
    DiagramMiscMixin
):
    @dataclass
    class DiagramData:
        path     : str    = None
        modified : bool   = False
        title    : str    = None
        sheet    : QSizeF = field(default_factory=QSizeF)
        margin   : float  = None
        content  : list   = field(default_factory=list)
        wip      : list   = field(default_factory=list)

    def __init__(self, title=None):
        self.data = self.DiagramData()
        self.data.modified = True
        self.data.title    = title
        self.data.sheet     = settings.prefs.file.new.sheet
        self.data.margin   = settings.prefs.file.new.margin
        self.data.content  = []
        self.data.wip      = []

    def setWindow(self, window):
        self.window = window

    def new(self, title, sheet = None, margin = None):
        self.data = self.DiagramData()
        self.data.modified = True
        self.data.title    = title
        self.data.sheet    = settings.prefs.file.new.sheet if sheet is None else sheet
        self.data.margin   = settings.prefs.file.new.margin if margin is None else margin
        self.data.content  = []
        self.data.wip      = []

        self.selected = []
        self.extents = self.data.sheet # empty diagram extents = sheet size
        # diagram now exists so enable all relevant slots
