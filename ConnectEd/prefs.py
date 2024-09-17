from PyQt6.QtCore import Qt, QSizeF, QMarginsF
from PyQt6.QtGui import QColor, QFont


empty = Qt.BrushStyle.NoBrush
solid = Qt.BrushStyle.SolidPattern

def Font(font, size, bold=False, italic=False, underline=False):
    r = QFont(font, size)
    r.setBold(bold)
    r.setItalic(italic)
    r.setUnderline(underline)
    return r

class MaxMin:
    def __init__(self, max, min):
        self.max = max
        self.min = min

class Prefs:
    class Dwg:
        class Line:
            def __init__(self, color, width=0):
                self.color = color
                self.width = width

        class Fill:
            def __init__(self, color=QColor(0,0,0), style=solid):
                self.color = color
                self.style = style

        class LineFill:
            def __init__(self, line, fill):
                self.line = line
                self.fill = fill

        class Text:
            def __init__(self, font, color, line=None):
                self.font  = font
                self.color = color
                self.line  = line

        class Border:
            def __init__(self, enable, line):
                self.enable = enable
                self.line   = line

        class Grid:
            def __init__(self, enable, line):
                self.enable = enable
                self.line   = line

        class Block:
            def __init__(
                self,
                line,
                fill,
                property
            ):
                self.line     = line
                self.fill     = fill
                self.property = property

        def __init__(
            self,
            background,
            selected,
            highlighted,
            moving,
            border,
            grid,
            block
        ):
            self.background  = background
            self.selected    = selected
            self.highlighted = highlighted
            self.moving      = moving
            self.border      = border
            self.grid        = grid
            self.block       = block

    class View:
        def __init__(self, zoomLimits, zoomFullMargin, panStep, wheelStep):
            self.zoomLimits     = zoomLimits
            self.zoomFullMargin = zoomFullMargin
            self.panStep        = panStep
            self.wheelStep      = wheelStep

    class Edit:
        class Grid:
            def __init__(self, enable, size):
                self.enable = enable
                self.size   = size

        class Select:
            def __init__(self, enclose):
                self.enclose = enclose

        def __init__(self, grid, select):
            self.grid   = grid
            self.select = select

    def __init__(self, dwg, view, edit):
        self.dwg  = dwg
        self.view = view
        self.edit = edit

prefs = Prefs(
    dwg = Prefs.Dwg(
        background  = QColor(24,24,24),
        selected = Prefs.Dwg.LineFill(
            Prefs.Dwg.Line(QColor(255,0,255)),
            Prefs.Dwg.Fill(QColor(32,0,32))
        ),
        highlighted = Prefs.Dwg.LineFill(
            Prefs.Dwg.Line(QColor(255,255,0)),
            Prefs.Dwg.Fill(QColor(32,32,0))
        ),
        moving = Prefs.Dwg.LineFill(
            Prefs.Dwg.Line(QColor(255,255,255)),
            Prefs.Dwg.Fill(QColor(32,32,32))
        ),
        border = Prefs.Dwg.Border(
            enable = True,
            line   = Prefs.Dwg.Line(QColor(0,255,0))
        ),
        grid = Prefs.Dwg.Grid(
            enable = True,
            line   = Prefs.Dwg.Line(QColor(100,100,100))
        ),
        block = Prefs.Dwg.Block(
            line     = Prefs.Dwg.Line(QColor(0,0,224)),
            fill     = Prefs.Dwg.Fill(QColor(0,0,32)),
            property = Prefs.Dwg.Text(
                font  = Font("Courier", 6),
                color = QColor(224,224,224),
                line  = None
            )
        )
    ),
    view = Prefs.View(
        zoomLimits     = MaxMin(16.0, 0.1),
        zoomFullMargin = QMarginsF(2, 2, 2, 2),
        panStep        = 0.125,
        wheelStep      = 120
    ),
    edit = Prefs.Edit(
        grid = Prefs.Edit.Grid(
            enable = True,
            size   = QSizeF(10,10)
        ),
        select = Prefs.Edit.Select(
            enclose = False
        )
    )
)
