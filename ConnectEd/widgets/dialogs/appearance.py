__all__ = ["CustomColorDialog", "FillDialog"]

from typing import Self, Optional
from collections import namedtuple

from PyQt6.QtCore    import Qt, QRect, QSize
from PyQt6.QtWidgets import QWidget, QDialog, QColorDialog, \
                            QLabel, QCheckBox, QComboBox, QPushButton, \
                            QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt6.QtGui     import QPainter, QColor, QPen, QBrush, \
                            QPixmap, QIcon, \
                            QFont, QFontMetrics

from ... import hub


class CustomColorDialog(QColorDialog):
    def __init__(
        self   : Self,
        color  : QColor,
        parent : Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Color")
        self.setOption(QColorDialog.ColorDialogOption.NoButtons, True)
        self.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
        self.setWindowTitle("Select Color")
        self.setCurrentColor(color)
        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.onOkClicked)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.onCancelClicked)
        layout = self.layout()
        self.xtra_row = QHBoxLayout()
        self.xtra_row.addStretch()
        self.xtra_row.addWidget(self.ok_button)
        self.xtra_row.addWidget(self.cancel_button)
        layout.addLayout(self.xtra_row)

    def onOkClicked(self : Self) -> None:
        self.accept()

    def onCancelClicked(self : Self) -> None:
        self.reject()

    def getColor(self : Self) -> QColor:
        return self.currentColor()

    def setColor(self : Self, color : Optional[QColor]) -> None:
        self.setCurrentColor(color)

ColorDef = namedtuple("ColorDef", ["name", "color"])

class ColorComboBox(QComboBox):
    COLORS = [
        ColorDef( "<default>"    , None                       ),
        ColorDef( "<custom>"     , None                       ),
        ColorDef( "Black"        , Qt.GlobalColor.black       ),
        ColorDef( "Dark Red"     , Qt.GlobalColor.darkRed     ),
        ColorDef( "Red"          , Qt.GlobalColor.red         ),
        ColorDef( "Dark Yellow"  , Qt.GlobalColor.darkYellow  ),
        ColorDef( "Yellow"       , Qt.GlobalColor.yellow      ),
        ColorDef( "Dark Green"   , Qt.GlobalColor.darkGreen   ),
        ColorDef( "Green"        , Qt.GlobalColor.green       ),
        ColorDef( "Dark Cyan"    , Qt.GlobalColor.darkCyan    ),
        ColorDef( "Cyan"         , Qt.GlobalColor.cyan        ),
        ColorDef( "Dark Blue"    , Qt.GlobalColor.darkBlue    ),
        ColorDef( "Blue"         , Qt.GlobalColor.blue        ),
        ColorDef( "Dark Magenta" , Qt.GlobalColor.darkMagenta ),
        ColorDef( "Magenta"      , Qt.GlobalColor.magenta     ),
        ColorDef( "Dark Gray"    , Qt.GlobalColor.darkGray    ),
        ColorDef( "Gray"         , Qt.GlobalColor.gray        ),
        ColorDef( "Light Gray"   , Qt.GlobalColor.lightGray   ),
        ColorDef( "White"        , Qt.GlobalColor.white       )
    ]

    color : Optional[QColor]

    def __init__(
        self    : Self,
        current : Optional[QColor],
        default : QColor,
        parent  : Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self.color   = current
        self.default = default
        for i, c in enumerate(self.COLORS):
            icon = self.getIcon(
                default if i == 0 else
                default if i == 1 and current is None else
                current if i == 1 and current is not None else
                c.color
            )
            self.addItem(icon, c.name)
        self.setCurrentIndex(self.getIndex(current))
        self.activated.connect(self.onSelection)

    def getIcon(self, color : QColor) -> QIcon:
        size = self.iconSize()
        pixmap = QPixmap(size.width(), size.height())
        pixmap.fill(color)
        return QIcon(pixmap)

    def getIndex(self, color : Optional[QColor]) -> int:
        if color is None:
            index = 0
        else:
            index = 1
            for i, c in enumerate(self.COLORS[2:]):
                if c.color == color:
                    index = i
                    break
        return index

    def getColor(self) -> QColor:
        return self.color

    def onSelection(self : Self, index : int) -> None:
        if index == 0:
            self.color = None
        elif index == 1:
            color_dialog = CustomColorDialog(
                self.default if self.color is None else self.color
            )
            if color_dialog.exec():
                self.color = color_dialog.getColor()
                icon = self.getIcon(self.color)
                self.setItemIcon(1, icon)
        else:
            self.color = self.COLORS[index].color

class LineStyleDef:
    name  : str
    style : Qt.PenStyle

    def __init__(self : Self, name : str, style : Qt.PenStyle) -> None:
        self.name  = name
        self.style = style

class LineStyleComboBox(QComboBox):
    STYLES = [
        LineStyleDef( "<default>"    , Qt.PenStyle.SolidLine      ),
        LineStyleDef( "<no line>"    , Qt.PenStyle.SolidLine      ),
        LineStyleDef( "Solid"        , Qt.PenStyle.SolidLine      ),
        LineStyleDef( "Dash"         , Qt.PenStyle.DashLine       ),
        LineStyleDef( "Dot"          , Qt.PenStyle.DotLine        ),
        LineStyleDef( "Dash Dot"     , Qt.PenStyle.DashDotLine    ),
        LineStyleDef( "Dash Dot Dot" , Qt.PenStyle.DashDotDotLine ),
    ]

    styles : list[LineStyleDef]
    style  : Optional[Qt.PenStyle]

    def __init__(
        self    : Self,
        current : Optional[Qt.PenStyle],
        default : Qt.PenStyle,
        parent  : Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self.styles = self.STYLES[:]
        self.setCurrentIndex(self.getIndex(current))
        self.styles[0].name = f"<default = {self.getName(default)}>"
        if hub.settings.get("display/theme") == "dark":
            bg = Qt.GlobalColor.black; fg = Qt.GlobalColor.white
        else:
            bg = Qt.GlobalColor.white; fg = Qt.GlobalColor.black
        for style_def in self.styles:
            icon = self.getIcon(style_def.style, fg, bg)
            self.addItem(icon, style_def.name)
        self.currentIndexChanged.connect(self.onSelection)

    def onSelection(self : Self, index : int) -> None:
        if index == 0:
            self.style = None
        else:
            self.style = self.styles[index].style

    def getIndex(self, style : Optional[Qt.PenStyle]) -> int:
        if style is None:
            return 0
        for i, style_def in enumerate(self.styles):
            if style_def.style == style:
                return i
        raise ValueError(f"Style {style} not found")

    def getName(self, style : Qt.PenStyle) -> str:
        for style_def in self.styles:
            if style_def.style == style:
                return style_def.name
        raise ValueError(f"Style {style} not found")

    def getIcon(self, style : Qt.PenStyle, fg : QColor, bg : QColor) -> QIcon:
        size = self.iconSize()
        pixmap = QPixmap(size.width(), size.height())
        pixmap.fill(bg)
        painter = QPainter(pixmap)
        painter.setPen(QPen(fg, 1, style))
        painter.drawLine(
            0, size.height() // 2, size.width(), size.height() // 2
        )
        painter.end()
        return QIcon(pixmap)

    def getStyle(self) -> Qt.PenStyle:
        if self.currentIndex() == 0:
            return None
        else:
            return self.styles[self.currentIndex()].style

class FillStyleDef:
    name  : str
    style : Qt.BrushStyle

    def __init__(self : Self, name : str, style : Qt.BrushStyle) -> None:
        self.name  = name
        self.style = style

class FillStyleComboBox(QComboBox):
    STYLES = [
        FillStyleDef( "<default>" , Qt.BrushStyle.NoBrush          ),
        FillStyleDef( "<no fill>" , Qt.BrushStyle.NoBrush          ),
        FillStyleDef( "Solid"     , Qt.BrushStyle.SolidPattern     ),
        FillStyleDef( "Dense1"    , Qt.BrushStyle.Dense1Pattern    ),
        FillStyleDef( "Dense2"    , Qt.BrushStyle.Dense2Pattern    ),
        FillStyleDef( "Dense3"    , Qt.BrushStyle.Dense3Pattern    ),
        FillStyleDef( "Dense4"    , Qt.BrushStyle.Dense4Pattern    ),
        FillStyleDef( "Dense5"    , Qt.BrushStyle.Dense5Pattern    ),
        FillStyleDef( "Dense6"    , Qt.BrushStyle.Dense6Pattern    ),
        FillStyleDef( "Dense7"    , Qt.BrushStyle.Dense7Pattern    ),
        FillStyleDef( "Hor"       , Qt.BrushStyle.HorPattern       ),
        FillStyleDef( "Ver"       , Qt.BrushStyle.VerPattern       ),
        FillStyleDef( "Cross"     , Qt.BrushStyle.CrossPattern     ),
        FillStyleDef( "BDiag"     , Qt.BrushStyle.BDiagPattern     ),
        FillStyleDef( "FDiag"     , Qt.BrushStyle.FDiagPattern     ),
        FillStyleDef( "DiagCross" , Qt.BrushStyle.DiagCrossPattern )
    ]

    styles : list[FillStyleDef]
    style  : Optional[Qt.BrushStyle]

    def __init__(
        self    : Self,
        current : Optional[Qt.BrushStyle],
        default : Qt.BrushStyle,
        parent  : Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self.styles = self.STYLES[:]
        self.setCurrentIndex(self.getIndex(current))
        self.styles[0].name = f"<default = {self.getName(default)}>"
        if hub.settings.get("display/theme") == "dark":
            bg = Qt.GlobalColor.black; fg = Qt.GlobalColor.white
        else:
            bg = Qt.GlobalColor.white; fg = Qt.GlobalColor.black
        for style_def in self.styles:
            icon = self.getIcon(style_def.style, fg, bg)
            self.addItem(icon, style_def.name)
        self.currentIndexChanged.connect(self.onSelection)

    def onSelection(self : Self, index : int) -> None:
        if index == 0:
            self.style = None
        else:
            self.style = self.styles[index].style

    def getIndex(self, style : Optional[Qt.BrushStyle]) -> int:
        if style is None:
            return 0
        for i, style_def in enumerate(self.styles):
            if style_def.style == style:
                return i
        raise ValueError(f"Style {style} not found")

    def getName(self, style : Qt.BrushStyle) -> str:
        for style_def in self.styles:
            if style_def.style == style:
                return style_def.name
        raise ValueError(f"Style {style} not found")

    def getIcon(
        self   : Self,
        style  : Qt.BrushStyle,
        fg     : QColor,
        bg     : QColor
    ) -> QIcon:
        size = self.iconSize()
        pixmap = QPixmap(size.width(), size.height())
        pixmap.fill(bg)
        painter = QPainter(pixmap)
        painter.fillRect(0, 0, size.width(), size.height(), QBrush(fg, style))
        painter.end()
        return QIcon(pixmap)

    def getStyle(self) -> Qt.BrushStyle:
        if self.currentIndex() == 0:
            return None
        else:
            return self.styles[self.currentIndex()].style

class FillDialog(QDialog):
    def __init__(
        self    : Self,
        current_color : Optional[QColor],
        default_color : QColor,
        current_style : Optional[Qt.BrushStyle],
        default_style : Qt.BrushStyle,
        parent  : Optional[QWidget] = None
    ) -> None:
        if isinstance(current_color, QColor):
            print("FillDialog current_color", current_color.red(), current_color.green(), current_color.blue())
        else:
            print("FillDialog current_color", current_color)
        print("FillDialog default_color", default_color.red(), default_color.green(), default_color.blue())
        super().__init__(parent)
        self.setWindowTitle("Fill")
        self.dialog_layout = QVBoxLayout()
        self.grid_layout = QGridLayout()
        self.color_label = QLabel("Color:")
        self.grid_layout.addWidget(
            self.color_label, 0, 0, Qt.AlignmentFlag.AlignRight
        )
        self.color_combo = ColorComboBox(
            current_color, default_color
        )
        self.grid_layout.addWidget(self.color_combo, 0, 1)
        self.style_label = QLabel("Style:")
        self.grid_layout.addWidget(
            self.style_label, 1, 0, Qt.AlignmentFlag.AlignRight
        )
        self.style_combo = FillStyleComboBox(
            current_style, default_style
        )
        self.grid_layout.addWidget(self.style_combo, 1, 1)
        self.dialog_layout.addLayout(self.grid_layout)
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.button_layout.addWidget(self.ok_button)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.cancel_button)
        self.dialog_layout.addLayout(self.button_layout)
        self.setLayout(self.dialog_layout)

    def getColor(self) -> QColor:
        return self.color_combo.getColor()

    def getStyle(self) -> Qt.BrushStyle:
        return self.style_combo.getStyle()

