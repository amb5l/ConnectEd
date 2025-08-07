from typing import Self, Optional
from dataclasses import dataclass

from PyQt6.QtCore    import Qt, QSize
from PyQt6.QtWidgets import QWidget, QDialog, QColorDialog, \
                            QLabel, QComboBox, QPushButton, QLineEdit, QGroupBox, \
                            QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt6.QtGui     import QPainter, QColor, QPen, QBrush, \
                            QPixmap, QIcon, QFontDatabase, QFont

from ...core.log import logger

from ...core.icon import getDefaultIconSize, getFgBgColors, \
                         SvgIconSingleton, CharIconSingleton

from ..drawing.items import ElementLineMixin, ElementFillMixin, ElementQuillMixin, \
                            LineSpec,LinePref, LinePrefDefault, LinePrefChange, \
                            FillSpec, FillPref, FillPrefDefault, FillPrefChange, \
                            QuillSpec, QuillPref, QuillPrefDefault, QuillPrefChange, \
                            Default, DEFAULT, NoChange, NO_CHANGE

from . import okCancelLayout

from ... import hub


@dataclass
class AppearanceSpec:
    line  : Optional[LineSpec]  = None
    fill  : Optional[FillSpec]  = None
    quill : Optional[QuillSpec] = None

@dataclass
class AppearancePref:
    line  : Optional[LinePref]  = None
    fill  : Optional[FillPref]  = None
    quill : Optional[QuillPref] = None

@dataclass
class AppearancePrefChange:
    line  : Optional[LinePrefChange]  = None
    fill  : Optional[FillPrefChange]  = None
    quill : Optional[QuillPrefChange] = None

CUSTOM_ICON_SIZE = QSize(getDefaultIconSize() * 2, getDefaultIconSize())

class NoChangeIcon(SvgIconSingleton):
    PATH = f"{hub.APP_ROOT}/resources/icons/no_change.svg"
    SIZE = CUSTOM_ICON_SIZE

class DefaultIcon(SvgIconSingleton):
    PATH = f"{hub.APP_ROOT}/resources/icons/default.svg"
    SIZE = CUSTOM_ICON_SIZE

class QueryIcon(CharIconSingleton):
    FONT_FAMILY = "Arial"
    CHAR = "?"
    SIZE = CUSTOM_ICON_SIZE

class CustomColorDialog(QColorDialog):
    def __init__(
        self   : Self,
        color  : QColor,
        parent : Optional[QWidget] = hub.main_window
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Color")
        self.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
        if isinstance(color, QColor):
            self.setCurrentColor(color)

    def getChoice(self : Self) -> QColor:
        return self.currentColor()

class ColorComboBox(QComboBox):
    COLORS = {
        "<no change>"  : NO_CHANGE,
        "<default>"    : DEFAULT,
        "<custom>"     : "placeholder",
        "Black"        : QColor(Qt.GlobalColor.black),
        "Dark Red"     : QColor(Qt.GlobalColor.darkRed),
        "Red"          : QColor(Qt.GlobalColor.red),
        "Dark Yellow"  : QColor(Qt.GlobalColor.darkYellow),
        "Yellow"       : QColor(Qt.GlobalColor.yellow),
        "Dark Green"   : QColor(Qt.GlobalColor.darkGreen),
        "Green"        : QColor(Qt.GlobalColor.green),
        "Dark Cyan"    : QColor(Qt.GlobalColor.darkCyan),
        "Cyan"         : QColor(Qt.GlobalColor.cyan),
        "Dark Blue"    : QColor(Qt.GlobalColor.darkBlue),
        "Blue"         : QColor(Qt.GlobalColor.blue),
        "Dark Magenta" : QColor(Qt.GlobalColor.darkMagenta),
        "Magenta"      : QColor(Qt.GlobalColor.magenta),
        "Dark Gray"    : QColor(Qt.GlobalColor.darkGray),
        "Gray"         : QColor(Qt.GlobalColor.gray),
        "Light Gray"   : QColor(Qt.GlobalColor.lightGray),
        "White"        : QColor(Qt.GlobalColor.white)
    }

    choice : Optional[ NoChange | Default | QColor ]

    def __init__(
        self      : Self,
        initial   : NoChange | Default | QColor,
        default   : Default | QColor,
        no_change : Optional[NoChange | Default | QColor] = None,
        parent    : Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self.setIconSize(CUSTOM_ICON_SIZE)
        default_icon = \
            self.getIcon(default) if isinstance(default, QColor) else \
            DefaultIcon().get()
        no_change_icon = \
            self.getIcon(no_change) if isinstance(no_change, QColor) else \
            default_icon if no_change is DEFAULT else \
            NoChangeIcon().get()
        custom = True
        custom_idx = None
        for k, v in self.COLORS.items():
            i = self.count()
            text = k
            match k:
                case "<no change>":
                    if no_change is None and initial is not NO_CHANGE:
                        continue
                    icon = no_change_icon
                case "<default>":
                    icon = default_icon
                case "<custom>":
                    custom_idx = i
                    icon = QueryIcon().get()
                case _:
                    icon = self.getIcon(v)
            self.addItem(icon, text)
            if initial == v:
                self.setCurrentIndex(i)
                custom = False
            elif initial is NO_CHANGE and k == "<no change>":
                self.setCurrentIndex(i)
                custom = False
            elif isinstance(initial, Default) and k == "<default>":
                self.setCurrentIndex(i)
                custom = False
        if isinstance(initial, QColor) and custom and custom_idx is not None:
            self.setCurrentIndex(custom_idx)
            self.setItemIcon(custom_idx, self.getIcon(initial))
        self.choice = initial
        self.activated.connect(self.onActivated)

    def onActivated(self : Self, index : int) -> None:
        selected_text = self.currentText()
        if selected_text == "<no change>":
            self.choice = NO_CHANGE
        elif selected_text == "<default>":
            self.choice = DEFAULT
        elif selected_text == "<custom>":
            dialog = CustomColorDialog(
                self.choice if isinstance(self.choice, QColor) else None
            )
            if dialog.exec():
                self.choice = dialog.getChoice()
                self.setItemIcon(index, self.getIcon(self.choice))
        else:
            self.choice = self.COLORS[selected_text]

    def getIcon(self : Self, color : QColor) -> QIcon:
        size = self.iconSize()
        pixmap = QPixmap(size.width(), size.height())
        pixmap.fill(color)
        with QPainter(pixmap) as painter:
            painter.fillRect(0, 0, size.width(), size.height(), color)
        return QIcon(pixmap)

    def getChoice(self) -> Optional[NoChange | Default | QColor]:
        return self.choice

class CustomLineWidthDialog(QDialog):
    def __init__(
        self    : Self,
        initial : Optional[float | int] = None,
        parent  : Optional[QWidget] = hub.main_window
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Line Width")
        self.dialog_layout = QVBoxLayout()
        self.width_layout = QHBoxLayout()
        self.width_label = QLabel("Width:")
        self.width_layout.addWidget(self.width_label)
        self.width_input = QLineEdit("" if initial is None else str(initial))
        self.width_layout.addWidget(self.width_input)
        self.dialog_layout.addLayout(self.width_layout)
        okCancelLayout(self)
        self.setLayout(self.dialog_layout)

    def getChoice(self) -> Optional[float]:
        try:
            return float(self.width_input.text())
        except:
            return None

class LineWidthComboBox(QComboBox):
    WIDTHS = {
        "<no change>" : NO_CHANGE,
        "<default>"   : DEFAULT,
        "<custom>"    : "placeholder",
        "1"           : 1,
        "2"           : 2,
        "3"           : 3
    }

    def __init__(
        self      : Self,
        initial   : NoChange | Default | float | int,
        default   : Default | float | int,
        no_change : Optional[NoChange | Default | float | int] = None,
        parent    : Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.setIconSize(CUSTOM_ICON_SIZE)
        if isinstance(default, float | int):
            default_icon = self.getIcon(default)
            default_str = f" = {default}"
        else:
            default_icon = DefaultIcon().get()
            default_str = ""
        if isinstance(no_change, float | int):
            no_change_icon = self.getIcon(no_change)
            no_change_str = f" = {no_change}"
        elif no_change is DEFAULT:
            no_change_icon = default_icon
            no_change_str = f" = default{default_str}"
        else:
            no_change_icon = NoChangeIcon().get()
            no_change_str = ""
        for i, (k, v) in enumerate(self.WIDTHS.items()):
            match k:
                case "<no change>":
                    if no_change is None and initial is not NO_CHANGE:
                        continue
                    icon = no_change_icon
                    text = f"<no change{no_change_str}>"
                case "<default>":
                    icon = default_icon
                    text = f"<default{default_str}>"
                case "<custom>":
                    icon = QueryIcon().get()
                    text = k
                case _:
                    icon = self.getIcon(v)
                    text = f"{v}"
            self.addItem(icon, text)
            if initial == v:
                self.setCurrentIndex(i)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.activated.connect(self.onActivated)

    def onActivated(self : Self, index : int) -> None:
        keys = list(self.WIDTHS.keys())
        if keys[index].startswith("<custom"):
            dialog = CustomLineWidthDialog()
            if dialog.exec():
                w = dialog.getChoice()
                self.setItemText(
                    index,
                    f"<custom = {w}>" if w is not None else "<custom>"
                )
                self.setItemIcon(
                    index,
                    QueryIcon().get() if w is None else self.getIcon(w)
                )

    def getIcon(self : Self, width : float | int) -> QIcon:
        fg, bg = getFgBgColors()
        size = self.iconSize()
        pixmap = QPixmap(size.width(), size.height())
        pixmap.fill(Qt.GlobalColor.transparent)
        with QPainter(pixmap) as painter:
            painter.fillRect(0, 0, size.width(), size.height(), bg)
            painter.setPen(QPen(fg, width, Qt.PenStyle.SolidLine))
            painter.drawLine(
                0, size.height() // 2, size.width() - 1, size.height() // 2
            )
        return QIcon(pixmap)

    def getChoice(self) -> Optional[float] | NoChange:
        text = self.currentText()
        if text.startswith("<no change"):
            r = NO_CHANGE
        elif text.startswith("<default"):
            r = DEFAULT
        else:
            try:
                r = float(text)
                if r < 0:
                    r = None
            except:
                r = None
        return r

class LineStyleComboBox(QComboBox):
    STYLES = {
        "<no change>"    : NO_CHANGE,
        "<default>"      : DEFAULT,
        "No Line"      : Qt.PenStyle.NoPen,
        "Solid"        : Qt.PenStyle.SolidLine,
        "Dash"         : Qt.PenStyle.DashLine,
        "Dot"          : Qt.PenStyle.DotLine,
        "Dash Dot"     : Qt.PenStyle.DashDotLine,
        "Dash Dot Dot" : Qt.PenStyle.DashDotDotLine
    }
    STYLES_REVERSE = {v: k for k, v in STYLES.items()}

    def __init__(
        self      : Self,
        initial   : NoChange | Default | Qt.PenStyle,
        default   : Default | Qt.PenStyle,
        no_change : Optional[NoChange | Default | Qt.PenStyle] = None,
        parent    : Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self.setIconSize(CUSTOM_ICON_SIZE)
        if isinstance(default, Qt.PenStyle):
            default_icon = self.getIcon(default)
            default_str = f" = {self.STYLES_REVERSE[default]}"
        else:
            default_icon = DefaultIcon().get()
            default_str = ""
        if isinstance(no_change, Qt.PenStyle):
            no_change_icon = self.getIcon(no_change)
            no_change_str = f" = {self.STYLES_REVERSE[no_change]}"
        elif no_change is DEFAULT:
            no_change_icon = default_icon
            no_change_str = f" = default{default_str}"
        else:
            no_change_icon = NoChangeIcon().get()
            no_change_str = ""
        for i, (k, v) in enumerate(self.STYLES.items()):
            match k:
                case "<no change>":
                    if no_change is None and initial is not NO_CHANGE:
                        continue
                    icon = no_change_icon
                    text = f"<no change{no_change_str}>"
                case "<default>":
                    icon = default_icon
                    text = f"<default{default_str}>"
                case _:
                    icon = self.getIcon(v)
                    text = f"{self.STYLES_REVERSE[v]}"
            self.addItem(icon, text)
            if initial == v:
                self.setCurrentIndex(i)

    def getIcon(self : Self, style : Qt.PenStyle) -> QIcon:
        fg, bg = getFgBgColors()
        size = self.iconSize()
        pixmap = QPixmap(size.width(), size.height())
        pixmap.fill(Qt.GlobalColor.transparent)
        with QPainter(pixmap) as painter:
            painter.fillRect(0, 0, size.width(), size.height(), bg)
            painter.setPen(QPen(fg, 1, style))
            painter.drawLine(
                0, size.height() // 2, size.width() - 1, size.height() // 2
            )
        return QIcon(pixmap)

    def getChoice(self) -> Optional[NoChange | Default | Qt.PenStyle]:
        text = self.currentText()
        if text.startswith("<no change"):
            return NO_CHANGE
        elif text.startswith("<default"):
            return DEFAULT
        else:
            keys = list(self.STYLES.keys())
            return self.STYLES[text] if text in keys else None

class FillStyleComboBox(QComboBox):
    STYLES = {
        "<no change>" : NO_CHANGE,
        "<default>"   : DEFAULT,
        "No Fill"     : Qt.BrushStyle.NoBrush,
        "Solid"       : Qt.BrushStyle.SolidPattern,
        "Dense1"      : Qt.BrushStyle.Dense1Pattern,
        "Dense2"      : Qt.BrushStyle.Dense2Pattern,
        "Dense3"      : Qt.BrushStyle.Dense3Pattern,
        "Dense4"      : Qt.BrushStyle.Dense4Pattern,
        "Dense5"      : Qt.BrushStyle.Dense5Pattern,
        "Dense6"      : Qt.BrushStyle.Dense6Pattern,
        "Dense7"      : Qt.BrushStyle.Dense7Pattern,
        "Hor"         : Qt.BrushStyle.HorPattern,
        "Ver"         : Qt.BrushStyle.VerPattern,
        "Cross"       : Qt.BrushStyle.CrossPattern,
        "BDiag"       : Qt.BrushStyle.BDiagPattern,
        "FDiag"       : Qt.BrushStyle.FDiagPattern,
        "DiagCross"   : Qt.BrushStyle.DiagCrossPattern
    }
    STYLES_REVERSE = {v: k for k, v in STYLES.items()}

    def __init__(
        self      : Self,
        initial   : NoChange | Default | Qt.BrushStyle,
        default   : Default | Qt.BrushStyle,
        no_change : Optional[NoChange | Default | Qt.BrushStyle] = None,
        parent    : Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self.setIconSize(CUSTOM_ICON_SIZE)
        if isinstance(default, Qt.BrushStyle):
            default_icon = self.getIcon(default)
            default_str = f" = {self.STYLES_REVERSE[default]}"
        else:
            default_icon = DefaultIcon().get()
            default_str = ""
        if isinstance(no_change, Qt.BrushStyle):
            no_change_icon = self.getIcon(no_change)
            no_change_str = f" = {self.STYLES_REVERSE[no_change]}"
        elif no_change is DEFAULT:
            no_change_icon = default_icon
            no_change_str = f" = default{default_str}"
        else:
            no_change_icon = NoChangeIcon().get()
            no_change_str = ""
        for i, (k, v) in enumerate(self.STYLES.items()):
            match k:
                case "<no change>":
                    if no_change is None and initial is not NO_CHANGE:
                        continue
                    icon = no_change_icon
                    text = f"<no change{no_change_str}>"
                case "<default>":
                    icon = default_icon
                    text = f"<default{default_str}>"
                case _:
                    icon = self.getIcon(v)
                    text = f"{self.STYLES_REVERSE[v]}"
            self.addItem(icon, text)
            if initial == v:
                self.setCurrentIndex(i)

    def getIcon(self : Self, style : Qt.BrushStyle) -> QIcon:
        fg, bg = getFgBgColors()
        size = self.iconSize()
        pixmap = QPixmap(size.width(), size.height())
        pixmap.fill(Qt.GlobalColor.transparent)
        with QPainter(pixmap) as painter:  # Use context manager for painter
            painter.fillRect(0, 0, size.width(), size.height(), bg)
            painter.setBrush(QBrush(fg, style))
            painter.drawRect(0, 0, size.width(), size.height())
        return QIcon(pixmap)

    def getChoice(self) -> Optional[NoChange | Default | Qt.PenStyle]:
        text = self.currentText()
        if text.startswith("<no change"):
            return NO_CHANGE
        elif text.startswith("<default"):
            return DEFAULT
        else:
            keys = list(self.STYLES.keys())
            return self.STYLES[text] if text in keys else None

class FontFamilyComboBox(QComboBox):
    def __init__(
        self      : Self,
        initial   : NoChange | Default | str,
        default   : Default | str,
        no_change : Optional[NoChange | Default | str] = None,
        parent    : Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        default_str = f" = {default}" if isinstance(default, str) else ""
        default_idx = 1
        no_change_str = \
            f" = {no_change}" if isinstance(no_change, str) else \
            f" = default{default_str}" if no_change is DEFAULT else \
            ""
        no_change_idx = 0
        self.families = []
        if no_change is not None or initial is NO_CHANGE:
            self.families.append(f"<no change{no_change_str}>")
        else:
            no_change_idx = -1
            default_idx   = 0
        self.families.append(f"<default{default_str}>")
        self.families.extend(sorted(QFontDatabase.families()))
        self.addItems(self.families)
        if initial is NO_CHANGE:
            self.setCurrentIndex(no_change_idx)
        elif initial is DEFAULT:
            self.setCurrentIndex(default_idx)
        elif isinstance(initial, str):
            self.setCurrentIndex(self.families.index(initial))

    def getChoice(self) -> NoChange | Default | str:
        text = self.currentText()
        if text.startswith("<no change"):
            return NO_CHANGE
        elif text.startswith("<default"):
            return DEFAULT
        else:
            return text

class FontSizeComboBox(QComboBox):
    SIZES : list[float] = [6, 7, 8, 9, 10, 12, 14, 16, 18, 24, 36, 48, 72]

    sizes : list[str | float]

    def __init__(
        self      : Self,
        initial   : NoChange | Default | float | int,
        default   : Default | float | int,
        no_change : Optional[NoChange | Default | float | int] = None,
        parent    : Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        default_str = \
            f" = {default}" if isinstance(default, float | int) else ""
        default_idx = 1
        no_change_str = \
            f" = {no_change}" if isinstance(no_change, float | int) else \
            f" = default{default_str}" if no_change is DEFAULT else \
            ""
        no_change_idx = 0
        self.sizes = []
        if no_change is not None or initial is NO_CHANGE:
            self.sizes.append(f"<no change{no_change_str}>")
        else:
            no_change_idx = -1
            default_idx   = 0
        self.sizes.append(f"<default{default_str}>")
        self.sizes.extend([str(size) for size in self.SIZES])
        self.addItems(self.sizes)
        if initial is NO_CHANGE:
            self.setCurrentIndex(no_change_idx)
        elif initial is DEFAULT:
            self.setCurrentIndex(default_idx)
        elif isinstance(initial, float | int) and initial in self.SIZES:
            self.setCurrentIndex(self.sizes.index(str(initial)))

    def getChoice(self) -> Optional[NoChange | Default | float]:
        text = self.currentText()
        if text.startswith("<no change"):
            return NO_CHANGE
        elif text.startswith("<default"):
            return DEFAULT
        else:
            try:
                return float(text)
            except:
                return None

class OnOffComboBox(QComboBox):
    def __init__(
        self      : Self,
        initial   : NoChange | Default | bool,
        default   : Default | bool,
        no_change : Optional[NoChange | Default | bool] = None,
        parent    : Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        default_str = \
            " = On"  if default is True else \
            " = Off" if default is False else \
            ""
        default_idx = 1
        no_change_str = \
            " = On"                    if no_change is True else \
            " = Off"                   if no_change is False else \
            f" = default{default_str}" if no_change is DEFAULT else \
            ""
        no_change_idx = 0
        if no_change is not None or initial is NO_CHANGE:
            self.addItem(f"<no change{no_change_str}>")
        else:
            no_change_idx = -1
            default_idx   = 0
        self.addItem(f"<default{default_str}>")
        self.addItem("Off")
        self.addItem("On")
        self.setCurrentIndex(
            default_idx + 2 if initial is True    else
            default_idx + 1 if initial is False   else
            default_idx     if initial is DEFAULT else
            no_change_idx
        )

    def getChoice(self) -> Optional[NoChange | Default | bool]:
        if self.currentIndex() < 0:
            return None
        if self.currentText().startswith("<no change"):
            return NO_CHANGE
        elif self.currentText().startswith("<default"):
            return DEFAULT
        else:
            return self.currentText().lower() == "on"

class LineAppearanceLayout(QGridLayout):
    color_label : QLabel
    color_combo : ColorComboBox
    width_label : QLabel
    width_combo : LineWidthComboBox
    style_label : QLabel
    style_combo : LineStyleComboBox

    def __init__(
        self      : Self,
        initial   : LinePrefChange,
        default   : LinePref,
        no_change : Optional[LinePrefChange] = None,
        parent    : Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self.choice    = initial
        self.no_change = no_change
        self.default   = default
        row = 0
        if initial.color is not None:
            self.color_label = QLabel("Color:")
            self.addWidget(self.color_label, row, 0)
            self.color_combo = ColorComboBox(
                initial.color,
                default.color,
                None if no_change is None else no_change.color,
            )
            self.addWidget(self.color_combo, row, 1)
            row += 1
        if initial.width is not None:
            self.width_label = QLabel("Width:")
            self.addWidget(self.width_label, row, 0)
            self.width_combo = LineWidthComboBox(
                initial.width,
                default.width,
                None if no_change is None else no_change.width,
            )
            self.addWidget(self.width_combo, row, 1)
            row += 1
        if initial.style is not None:
            self.style_label = QLabel("Style:")
            self.addWidget(self.style_label, row, 0)
            self.style_combo = LineStyleComboBox(
                initial.style,
                default.style,
                None if no_change is None else no_change.style,
            )
            self.addWidget(self.style_combo, row, 1)
        if hasattr(self, 'color_combo') and hasattr(self, 'style_combo'):
            self.color_combo.activated.connect(self._onColorChanged)
        if hasattr(self, 'width_combo') and hasattr(self, 'style_combo'):
            self.width_combo.activated.connect(self._onWidthChanged)

    def _onColorChanged(self : Self) -> None:
        color = self.color_combo.getChoice()
        style = self.style_combo.getChoice()
        if color not in (NO_CHANGE, DEFAULT) and style in (DEFAULT, Qt.PenStyle.NoPen):
            for i in range(self.style_combo.count()):
                if self.style_combo.itemText(i) == "Solid":
                    self.style_combo.setCurrentIndex(i)
                    break

    def _onWidthChanged(self : Self) -> None:
        width = self.width_combo.getChoice()
        style = self.style_combo.getChoice()
        if width not in (NO_CHANGE, DEFAULT) and style in (DEFAULT, Qt.PenStyle.NoPen):
            for i in range(self.style_combo.count()):
                if self.style_combo.itemText(i) == "Solid":
                    self.style_combo.setCurrentIndex(i)
                    break

    def getChoice(self : Self) -> LinePrefChange:
        r = LinePrefChange()
        if hasattr(self, "color_combo"):
            r.color = self.color_combo.getChoice()
        if hasattr(self, "width_combo"):
            r.width = self.width_combo.getChoice()
        if hasattr(self, "style_combo"):
            r.style = self.style_combo.getChoice()
        return r

class FillAppearanceLayout(QGridLayout):
    color_label : QLabel
    color_combo : ColorComboBox
    style_label : QLabel
    style_combo : FillStyleComboBox

    def __init__(self : Self,
        initial   : FillPrefChange,
        default   : FillPref,
        no_change : Optional[FillPrefChange] = None,
        parent    : Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        row = 0
        if initial.color is not None:
            self.color_label = QLabel("Color:")
            self.addWidget(self.color_label, row, 0)
            self.color_combo = ColorComboBox(
                initial.color,
                default.color,
                None if no_change is None else no_change.color,
            )
            self.addWidget(self.color_combo, row, 1)
            row += 1
        if initial.style is not None:
            self.style_label = QLabel("Style:")
            self.addWidget(self.style_label, row, 0)
            self.style_combo = FillStyleComboBox(
                initial.style,
                default.style,
                None if no_change is None else no_change.style,
            )
            self.addWidget(self.style_combo, row, 1)
        if hasattr(self, 'color_combo') and hasattr(self, 'style_combo'):
            self.color_combo.activated.connect(self._onColorChanged)
        if hasattr(self, 'width_combo') and hasattr(self, 'style_combo'):
            self.width_combo.activated.connect(self._onWidthChanged)

    def _onColorChanged(self : Self) -> None:
        """Automatically set SolidLine when color is specified and style is NoPen."""
        color = self.color_combo.getChoice()
        style = self.style_combo.getChoice()

        if color not in (NO_CHANGE, DEFAULT) and style in (DEFAULT, Qt.PenStyle.NoPen):
            for i in range(self.style_combo.count()):
                if self.style_combo.itemText(i) == "Solid":
                    self.style_combo.setCurrentIndex(i)
                    break

    def _onWidthChanged(self : Self) -> None:
        """Automatically set SolidLine when width is specified and style is NoPen."""
        width = self.width_combo.getChoice()
        style = self.style_combo.getChoice()

        if width not in (NO_CHANGE, DEFAULT) and style in (DEFAULT, Qt.PenStyle.NoPen):
            for i in range(self.style_combo.count()):
                if self.style_combo.itemText(i) == "Solid":
                    self.style_combo.setCurrentIndex(i)
                    break

    def getChoice(self : Self) -> FillPrefChange:
        r = FillPrefChange()
        if hasattr(self, "color_combo"):
            r.color = self.color_combo.getChoice()
        if hasattr(self, "style_combo"):
            r.style = self.style_combo.getChoice()
        return r

class TextAppearanceLayout(QVBoxLayout):
    no_change       : QuillPrefChange
    default         : QuillPref
    options_layout  : QGridLayout
    color_label     : QLabel
    color_combo     : ColorComboBox
    family_label    : QLabel
    family_combo    : FontFamilyComboBox
    size_label      : QLabel
    size_combo      : FontSizeComboBox
    bold_label      : QLabel
    bold_combo      : OnOffComboBox
    italic_label    : QLabel
    italic_combo    : OnOffComboBox
    underline_label : QLabel
    underline_combo : OnOffComboBox
    preview         : QLabel

    def __init__(self : Self,
        initial   : QuillPrefChange | QuillPref,
        default   : QuillPref | QuillSpec,
        no_change : Optional[QuillPrefChange] = None,
        parent    : Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self.no_change = no_change
        self.default   = default
        self.options_layout = QGridLayout()
        row = 0
        if initial.color is not None:
            self.color_label = QLabel("Color:")
            self.options_layout.addWidget(self.color_label, row, 0)
            self.color_combo = ColorComboBox(
                initial.color,
                default.color,
                None if no_change is None else no_change.color,
            )
            self.options_layout.addWidget(self.color_combo, row, 1)
            row += 1
        if initial.family is not None:
            self.family_label = QLabel("Family:")
            self.options_layout.addWidget(self.family_label, row, 0)
            self.family_combo = FontFamilyComboBox(
                initial.family,
                default.family,
                None if no_change is None else no_change.family,
            )
            self.options_layout.addWidget(self.family_combo, row, 1)
            row += 1
        if initial.size is not None:
            self.size_label = QLabel("Size:")
            self.options_layout.addWidget(self.size_label, row, 0)
            self.size_combo = FontSizeComboBox(
                initial.size,
                default.size,
                None if no_change is None else no_change.size,
            )
            self.options_layout.addWidget(self.size_combo, row, 1)
            row += 1
        if initial.bold is not None:
            self.bold_label = QLabel("Bold:")
            self.options_layout.addWidget(self.bold_label, row, 0)
            self.bold_combo = OnOffComboBox(
                initial.bold,
                default.bold,
                None if no_change is None else no_change.bold,
            )
            self.options_layout.addWidget(self.bold_combo, row, 1)
            row += 1
        if initial.italic is not None:
            self.italic_label = QLabel("Italic:")
            self.options_layout.addWidget(self.italic_label, row, 0)
            self.italic_combo = OnOffComboBox(
                initial.italic,
                default.italic,
                None if no_change is None else no_change.italic,
            )
            self.options_layout.addWidget(self.italic_combo, row, 1)
            row += 1
        if initial.underline is not None:
            self.underline_label = QLabel("Underline:")
            self.options_layout.addWidget(self.underline_label, row, 0)
            self.underline_combo = OnOffComboBox(
                initial.underline,
                default.underline,
                None if no_change is None else no_change.underline,
            )
            self.options_layout.addWidget(self.underline_combo, row, 1)
        self.addLayout(self.options_layout)
        self.preview = QLabel("Sample Text")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumHeight(40)
        self.updatePreview()
        self.addWidget(self.preview)
        self.family_combo.activated.connect(self.updatePreview)
        self.bold_combo.activated.connect(self.updatePreview)
        self.italic_combo.activated.connect(self.updatePreview)
        self.underline_combo.activated.connect(self.updatePreview)

    def updatePreview(self : Self):
        family    = self.family_combo.getChoice()
        family    = self.default.family   if family is DEFAULT else \
                    self.no_change.family if family is NO_CHANGE else \
                    family
        bold      = self.bold_combo.getChoice()
        bold      = self.default.bold   if bold is DEFAULT else \
                    self.no_change.bold if bold is NO_CHANGE else \
                    bold
        italic    = self.italic_combo.getChoice()
        italic    = self.default.italic if italic is DEFAULT else \
                    self.no_change.italic if italic is NO_CHANGE else \
                    italic
        underline = self.underline_combo.getChoice()
        underline = self.default.underline if underline is DEFAULT else \
                    self.no_change.underline if underline is NO_CHANGE else \
                    underline
        if family    is DEFAULT or family    is NO_CHANGE \
        or bold      is DEFAULT or bold      is NO_CHANGE \
        or italic    is DEFAULT or italic    is NO_CHANGE \
        or underline is DEFAULT or underline is NO_CHANGE:
            self.preview.setText("") # options are ambiguous
        else:
            font = QFont()
            font.setFamily(family)
            font.setPointSizeF(24.0) # TODO scale with dialog, or use settings?
            font.setBold(bold)
            font.setItalic(italic)
            font.setUnderline(underline)
            self.preview.setFont(font)
            self.preview.setText("Sample Text")

    def getChoice(self : Self) -> QuillPrefChange:
        r = QuillPrefChange()
        if hasattr(self, "color_combo"):
            r.color = self.color_combo.getChoice()
        if hasattr(self, "family_combo"):
            r.family = self.family_combo.getChoice()
        if hasattr(self, "size_combo"):
            r.size = self.size_combo.getChoice()
        if hasattr(self, "bold_combo"):
            r.bold = self.bold_combo.getChoice()
        if hasattr(self, "italic_combo"):
            r.italic = self.italic_combo.getChoice()
        if hasattr(self, "underline_combo"):
            r.underline = self.underline_combo.getChoice()
        return r

class AppearanceDialog(QDialog):
    _dialog_layout    : QVBoxLayout
    _line_group_box   : Optional[QGroupBox]
    _line_layout      : Optional[LineAppearanceLayout]
    _fill_group_box   : Optional[QGroupBox]
    _fill_layout      : Optional[FillAppearanceLayout]
    _text_group_box   : Optional[QGroupBox]
    _text_layout      : Optional[TextAppearanceLayout]
    _ok_cancel_layout : QHBoxLayout
    _ok_button        : QPushButton
    _cancel_button    : QPushButton

    def __init__(
        self     : Self,
        elements : list[ElementLineMixin | ElementFillMixin |ElementQuillMixin]
    ) -> None:
        super().__init__(hub.main_window)
        initial   = AppearancePrefChange()
        no_change = AppearancePrefChange()
        default   = AppearanceSpec()
        for element in elements:
            for cat_name in ["line", "fill", "quill"]:
                if not hasattr(element, cat_name):
                    continue
                cat = getattr(element, cat_name)
                if cat is None:
                    continue
                pref = cat.getPref()
                for subcat_name in \
                 ["color", "width", "style"] if cat_name == "line" else \
                 ["color", "style"] if cat_name == "fill" else \
                 ["color", "family", "size", "bold", "italic", "underline"]:
                    subcat = getattr(pref, subcat_name)
                    if subcat is None:
                        logger.error(f"{cat_name}/{subcat_name} is None for element {element}")
                        continue
                    # populate no_change values
                    n_cat = getattr(no_change, cat_name)
                    if n_cat is None:
                        n_cat = LinePrefChange() if cat_name == "line" else \
                                FillPrefChange() if cat_name == "fill" else \
                                QuillPrefChange() if cat_name == "quill" else \
                                None
                        setattr(no_change, cat_name, n_cat)
                    n_subcat = getattr(n_cat, subcat_name)
                    if n_subcat is None:
                        n_subcat = subcat
                    elif n_subcat != subcat:
                        n_subcat = NO_CHANGE
                    setattr(n_cat, subcat_name, n_subcat)
                    # populate initial values
                    i_cat = getattr(initial, cat_name)
                    if i_cat is None:
                        i_cat = LinePrefChange() if cat_name == "line" else \
                                FillPrefChange() if cat_name == "fill" else \
                                QuillPrefChange() if cat_name == "quill" else \
                                None
                        setattr(initial, cat_name, i_cat)
                    i_subcat = getattr(i_cat, subcat_name)
                    if i_subcat is None:
                        i_subcat = subcat
                    elif i_subcat != subcat:
                        i_subcat = NO_CHANGE
                    setattr(i_cat, subcat_name, i_subcat)
                    # populate default values
                    d_cat = getattr(element, cat_name).getDefaults()
                    if d_cat is None:
                        logger.error(f"{cat_name} is None in defaults for element {element}")
                        continue
                    if not hasattr(d_cat, subcat_name):
                        logger.error(f"No {cat_name}/{subcat_name} attribute in defaults for element {element}")
                        continue
                    d_subcat = getattr(d_cat, subcat_name)
                    if d_subcat is None:
                        logger.error(f"{cat_name}/{subcat_name} is None in defaults for element {element}")
                        continue
                    v_cat = getattr(default, cat_name)
                    if v_cat is None:
                        v_cat = LinePrefDefault() if cat_name == "line" else \
                                FillPrefDefault() if cat_name == "fill" else \
                                QuillPrefDefault() if cat_name == "quill" else \
                                None
                        setattr(default, cat_name, v_cat)
                    v_subcat = getattr(v_cat, subcat_name)
                    if v_subcat is None:
                        v_subcat = d_subcat
                    elif d_subcat != v_subcat:
                        v_subcat = DEFAULT
                    setattr(v_cat, subcat_name, v_subcat)
        categories = \
            (0 if initial.line  is None else 1) + \
            (0 if initial.fill  is None else 1) + \
            (0 if initial.quill is None else 1)
        if categories == 0:
            logger.warning("No appearance data found in element(s)")
            return
        if categories > 1:
            title = "Appearance"
        else:
            title = (
                "Line Appearance" if initial.line is not None else
                "Fill Appearance" if initial.fill is not None else
                "Text Appearance"
            )
        if len(elements) > 1:
            title += f" ({len(elements)} elements)"
        self.setWindowTitle(title)
        self._dialog_layout = QVBoxLayout()
        if initial.line is not None:
            self.line_group_box = QGroupBox("Line") if categories > 1 else None
            self._line_layout = LineAppearanceLayout(
                initial.line,
                default.line,
                no_change.line
            )
            if categories > 1:
                self.line_group_box.setLayout(self._line_layout)
                self._dialog_layout.addWidget(self.line_group_box)
            else:
                self._dialog_layout.addLayout(self._line_layout)
        else:
            self.line_group_box = None
            self._line_layout    = None
        if initial.fill is not None:
            self._fill_group_box = QGroupBox("Fill") if categories > 1 else None
            self._fill_layout = FillAppearanceLayout(
                initial.fill,
                default.fill,
                no_change.fill
            )
            if categories > 1:
                self._fill_group_box.setLayout(self._fill_layout)
                self._dialog_layout.addWidget(self._fill_group_box)
            else:
                self._dialog_layout.addLayout(self._fill_layout)
        else:
            self._fill_group_box = None
            self._fill_layout    = None
        if initial.quill is not None:
            self._text_group_box = QGroupBox("Text") if categories > 1 else None
            self._text_layout = TextAppearanceLayout(
                initial.quill,
                default.quill,
                no_change.quill
            )
            if categories > 1:
                self._text_group_box.setLayout(self._text_layout)
                self._dialog_layout.addWidget(self._text_group_box)
            else:
                self._dialog_layout.addLayout(self._text_layout)
        else:
            self._text_group_box = None
            self._text_layout    = None
        okCancelLayout(self)
        self.setLayout(self._dialog_layout)

    def _adjustComboBoxWidths(self : Self) -> None:
        """Find all combo boxes in the dialog and set them to the width of the widest one."""
        combo_boxes = []

        # Collect all combo boxes from all layouts
        if self._line_layout is not None:
            for attr_name in ['color_combo', 'width_combo', 'style_combo']:
                if hasattr(self._line_layout, attr_name):
                    combo_boxes.append(getattr(self._line_layout, attr_name))

        if self._fill_layout is not None:
            for attr_name in ['color_combo', 'style_combo']:
                if hasattr(self._fill_layout, attr_name):
                    combo_boxes.append(getattr(self._fill_layout, attr_name))

        if self._text_layout is not None:
            for attr_name in ['color_combo', 'family_combo', 'size_combo',
                            'bold_combo', 'italic_combo', 'underline_combo']:
                if hasattr(self._text_layout, attr_name):
                    combo_boxes.append(getattr(self._text_layout, attr_name))

        if not combo_boxes:
            return

        # Find the maximum width
        max_width = 0
        for combo in combo_boxes:
            # Get the minimum size hint and actual size
            size_hint = combo.sizeHint()
            current_width = max(size_hint.width(), combo.width())
            max_width = max(max_width, current_width)

        # Set all combo boxes to the maximum width
        for combo in combo_boxes:
            combo.setMinimumWidth(max_width)

    def showEvent(self, event):
        """Override showEvent to adjust combo box widths after layout is complete."""
        super().showEvent(event)
        # Use QTimer.singleShot to defer the width adjustment until after the event loop
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(0, self._adjustComboBoxWidths)

    def getChoice(self : Self) -> AppearancePrefChange:
        r = AppearancePrefChange()
        if self._line_layout is not None:
            r.line = self._line_layout.getChoice()
        if self._fill_layout is not None:
            r.fill = self._fill_layout.getChoice()
        if self._text_layout is not None:
            r.quill = self._text_layout.getChoice()
        return r
