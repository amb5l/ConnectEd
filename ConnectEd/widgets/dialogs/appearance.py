__all__ = ["AppearanceDialog"]

from typing import Self, Optional

from PyQt6.QtCore    import Qt, QSize
from PyQt6.QtWidgets import QWidget, QDialog, QColorDialog, \
                            QLabel, QComboBox, QPushButton, QLineEdit, QGroupBox, \
                            QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt6.QtGui     import QPainter, QColor, QPen, QBrush, \
                            QPixmap, QIcon, QFontDatabase

from ...core import logger

from ...core.icon import getDefaultIconSize, getFgBgColors, \
                         SvgIconSingleton, CharIconSingleton

from ..drawing.items import ElementMixin, AppearanceSpec, AppearanceSpecChange, \
                            AppearancePref, AppearancePrefChange, \
                            LinePrefChange, FillPrefChange, TextPrefChange, \
                            Default, DEFAULT, NoChange, NO_CHANGE

from ... import hub


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
        current   : Optional[NoChange | Default | QColor],
        no_change : Optional[NoChange | Default | QColor],
        default   : Optional[NoChange | QColor],
        parent    : Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self.setIconSize(CUSTOM_ICON_SIZE)
        default_icon = self.getIcon(default) if isinstance(default, QColor) \
            else DefaultIcon().get()
        for i, (k, v) in enumerate(self.COLORS.items()):
            if k == "<no change>":
                if no_change is DEFAULT:
                    icon = default_icon
                elif isinstance(no_change, QColor):
                    icon = self.getIcon(no_change)
                else:
                    icon = NoChangeIcon().get()
            elif k == "<default>":
                icon = default_icon
            elif k == "<custom>":
                icon = QueryIcon().get()
            else:
                icon = self.getIcon(v)
            self.addItem(icon, k)
            if current is not None and current == v:
                self.setCurrentIndex(i)
        if isinstance(current, QColor) and self.currentIndex() == -1:
            self.setCurrentIndex(2) # custom
            self.setItemIcon(2, self.getIcon(current))
        self.choice = current
        self.activated.connect(self.onActivated)

    def onActivated(self : Self, index : int) -> None:
        keys = list(self.COLORS.keys())
        if keys[index] == "<no change>":
            self.choice = NO_CHANGE
        elif keys[index] == "<default>":
            self.choice = DEFAULT
        elif keys[index] == "<custom>":
            dialog = CustomColorDialog(
                self.choice if isinstance(self.choice, QColor) else None
            )
            if dialog.exec():
                self.choice = dialog.getChoice()
                self.setItemIcon(index, self.getIcon(self.choice))
        else:
            self.choice = self.COLORS[keys[index]]

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
        self      : Self,
        width     : Optional[float | int] = None,
        parent    : Optional[QWidget] = hub.main_window
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Line Width")
        self.dialog_layout = QVBoxLayout()
        self.width_layout = QHBoxLayout()
        self.width_label = QLabel("Width:")
        self.width_layout.addWidget(self.width_label)
        self.width_input = QLineEdit(str(width) if width is not None else "")
        self.width_layout.addWidget(self.width_input)
        self.dialog_layout.addLayout(self.width_layout)
        self.ok_cancel_layout = QHBoxLayout()
        self.ok_cancel_layout.addStretch()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_cancel_layout.addWidget(self.ok_button)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.ok_cancel_layout.addWidget(self.cancel_button)
        self.dialog_layout.addLayout(self.ok_cancel_layout)
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
        current   : Optional[NoChange | Default | float | int],
        no_change : Optional[NoChange | Default | float | int],
        default   : Optional[NoChange | float | int],
        parent    : Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.setIconSize(CUSTOM_ICON_SIZE)
        default_icon = self.getIcon(default) if isinstance(default, float | int) \
            else DefaultIcon().get()
        for i, (k, v) in enumerate(self.WIDTHS.items()):
            text = k
            if k == "<no change>":
                if no_change is DEFAULT:
                    if isinstance(default, float | int):
                        text = f"<no change = default = {default}>"
                    else:
                        text = "<no change = default>"
                    icon = default_icon
                elif isinstance(no_change, float | int):
                    text = f"<no change = {no_change}>"
                    icon = self.getIcon(no_change)
                else:
                    icon = NoChangeIcon().get()
            elif k == "<default>":
                if isinstance(default, float | int):
                    text = f"<default = {default}>"
                icon = default_icon
            elif k == "<custom>":
                icon = QueryIcon().get()
            else:
                icon = self.getIcon(v)
            self.addItem(icon, text)
            if current is not None and current == v:
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
        current   : Optional[NoChange | Default | Qt.PenStyle],
        no_change : Optional[NoChange | Default | Qt.PenStyle],
        default   : Optional[NoChange | Qt.PenStyle],
        parent    : Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self.setIconSize(CUSTOM_ICON_SIZE)
        default_icon = self.getIcon(default) if isinstance(default, Qt.PenStyle) \
            else DefaultIcon().get()
        for i, (k, v) in enumerate(self.STYLES.items()):
            text = k
            if k == "<no change>":
                if no_change is DEFAULT:
                    text = "<no change = default>"
                    icon = default_icon
                elif isinstance(no_change, Qt.PenStyle):
                    text = f"<no change = {self.STYLES_REVERSE[no_change]}>"
                    icon = self.getIcon(no_change)
                else:
                    icon = NoChangeIcon().get()
            elif k == "<default>":
                if isinstance(default, Qt.PenStyle):
                    text = f"<default = {self.STYLES_REVERSE[default]}>"
                icon = default_icon
            else:
                icon = self.getIcon(v)
            self.addItem(icon, text)
            if current is not None and current == v:
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
        current   : Optional[NoChange | Default | Qt.BrushStyle],
        no_change : Optional[NoChange | Default | Qt.BrushStyle],
        default   : Optional[NoChange | Qt.BrushStyle],
        parent    : Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self.setIconSize(CUSTOM_ICON_SIZE)
        default_icon = self.getIcon(default) if isinstance(default, Qt.BrushStyle) \
            else DefaultIcon().get()
        for i, (k, v) in enumerate(self.STYLES.items()):
            text = k
            if k == "<no change>":
                if no_change is DEFAULT:
                    text = "<no change = default>"
                    icon = default_icon
                elif isinstance(no_change, Qt.BrushStyle):
                    text = f"<no change = {self.STYLES_REVERSE[no_change]}>"
                    icon = self.getIcon(no_change)
                else:
                    icon = NoChangeIcon().get()
            elif k == "<default>":
                if isinstance(default, Qt.BrushStyle):
                    text = f"<default = {self.STYLES_REVERSE[default]}>"
                icon = default_icon
            else:
                icon = self.getIcon(v)
            self.addItem(icon, text)
            if current is not None and current == v:
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
        current   : Optional[NoChange | Default | str],
        no_change : Optional[NoChange | Default | str],
        default   : Optional[NoChange | str],
        parent    : Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        no_change_str = f" = {no_change}" if isinstance(no_change, str) else \
                        f" = default" if no_change is DEFAULT else \
                        ""
        default_str = f" = {default}" if isinstance(default, str) else \
                      ""
        self.families = []
        self.families.append(f"<no change{no_change_str}>")
        self.families.append(f"<default{default_str}>")
        self.families.extend(sorted(QFontDatabase.families()))
        self.addItems(self.families)
        if current is NO_CHANGE:
            self.setCurrentIndex(0)
        elif current is DEFAULT:
            self.setCurrentIndex(1)
        elif isinstance(current, str):
            self.setCurrentIndex(self.families.index(current))

    def getChoice(self) -> Optional[NoChange | Default | str]:
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
        current   : Optional[NoChange | Default | float | int],
        no_change : Optional[NoChange | Default | float | int],
        default   : Optional[NoChange | float | int],
        parent    : Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        no_change_str = f" = {no_change}" if isinstance(no_change, float | int) else \
                        f" = default" if no_change is DEFAULT else \
                        ""
        default_str = f" = {default}" if isinstance(default, float | int) else \
                      ""
        self.sizes = []
        self.sizes.append(f"<no change{no_change_str}>")
        self.sizes.append(f"<default{default_str}>")
        self.sizes.extend([str(size) for size in self.SIZES])
        self.addItems(self.sizes)
        if current is NO_CHANGE:
            self.setCurrentIndex(0)
        elif current is DEFAULT:
            self.setCurrentIndex(1)
        elif isinstance(current, float | int) and current in self.SIZES:
            self.setCurrentIndex(self.sizes.index(str(current)))

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
        current   : Optional[NoChange | Default | bool],
        no_change : Optional[NoChange | Default | bool],
        default   : Optional[NoChange | bool],
        parent    : Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        no_change_str = " (On)"      if no_change is True else \
                        " (Off)"     if no_change is False else \
                        " (default)" if no_change is DEFAULT else \
                        ""
        default_str = " (On)"  if default is True else \
                      " (Off)" if default is False else \
                      ""
        self.addItem(f"no change{no_change_str}")
        self.addItem(f"default{default_str}")
        self.addItem("Off")
        self.addItem("On")
        self.setCurrentIndex(
            3 if current is True    else
            2 if current is False   else
            1 if current is DEFAULT else
            0
        )

    def getChoice(self) -> Optional[NoChange | Default | bool]:
        if self.currentIndex() < 0:
            return None
        return [NO_CHANGE, DEFAULT, False, True][self.currentIndex()]

class AppearanceDialog(QDialog):
    _default_values   : AppearanceSpec
    _no_change_values : AppearancePref
    _choice           : AppearancePrefChange

    def __init__(
        self     : Self,
        elements : list[ElementMixin],
        parent   : Optional[QWidget] = hub.main_window
    ) -> None:
        super().__init__(parent)
        self.choice = AppearancePrefChange()
        no_change_values = AppearancePrefChange()
        default_values = AppearanceSpecChange()
        for element in elements:
            for attr in ["line", "fill", "text"]:
                if not hasattr(element, attr):
                    continue
                ea = getattr(element, attr) # element.attr
                if ea is None:
                    continue
                for subattr in \
                 ["color", "width", "style"] if attr == "line" else \
                 ["color", "style"] if attr == "fill" else \
                 ["color", "family", "size", "bold", "italic", "underline"]:
                    ea = getattr(element, attr) # element.attr
                    if not hasattr(ea, subattr):
                        logger.error(f"{attr}.{subattr} missing for element {element}")
                        continue
                    es = getattr(ea, subattr) # element.attr.subattr
                    if es is None:
                        logger.error(f"{attr}.{subattr} is None for element {element}")
                        continue
                    na = getattr(no_change_values, attr) # no_change_values.attr
                    if na is None:
                        na = LinePrefChange() if attr == "line" else \
                             FillPrefChange() if attr == "fill" else \
                             TextPrefChange() if attr == "text" else \
                             None
                        setattr(no_change_values, attr, na)
                    ns = getattr(na, subattr) # no_change_values.attr.subattr
                    if ns is None:
                        ns = es
                    elif es != ns:
                        ns = NO_CHANGE
                    setattr(na, subattr, ns)
                    ca = getattr(self.choice, attr) # choice.attr
                    if ca is None:
                        ca = LinePrefChange() if attr == "line" else \
                             FillPrefChange() if attr == "fill" else \
                             TextPrefChange() if attr == "text" else \
                             None
                        setattr(self.choice, attr, ca)
                    cs = getattr(ca, subattr) # choice.attr.subattr
                    if cs is None:
                        cs = es
                    elif es != cs:
                        cs = NO_CHANGE
                    setattr(ca, subattr, cs)
                    d = element.getDefaults()
                    if not hasattr(d, attr):
                        logger.error(f"No {attr} defaults for element {element}")
                        continue
                    da = getattr(d, attr) # defaults.attr
                    if not hasattr(da, subattr):
                        logger.error(f"No {attr}.{subattr} attribute in defaults for element {element}")
                        continue
                    ds = getattr(da, subattr) # defaults.attr.subattr
                    if ds is None:
                        logger.error(f"No {subattr} attribute in defaults for element {element}")
                        continue
                    va = getattr(default_values, attr) # default_values.attr
                    if va is None:
                        va = LinePrefChange() if attr == "line" else \
                             FillPrefChange() if attr == "fill" else \
                             TextPrefChange() if attr == "text" else \
                             None
                        setattr(default_values, attr, va)
                    vs = getattr(va, subattr) # default_values.attr.subattr
                    if vs is None:
                        vs = ds
                    elif ds != vs:
                        vs = NO_CHANGE
                    setattr(va, subattr, vs)
        categories = \
            (0 if self.choice.line is None else 1) + \
            (0 if self.choice.fill is None else 1) + \
            (0 if self.choice.text is None else 1)
        if categories == 0:
            logger.warning("No appearance data found in element(s)")
            return
        self.dialog_layout = QVBoxLayout()
        if categories > 1:
            title = "Appearance"
        else:
            title = (
                "Line Appearance" if self.choice.line is not None else
                "Fill Appearance" if self.choice.fill is not None else
                "Text Appearance"
            )
        if len(elements) > 1:
            title += f" ({len(elements)} elements)"
        self.setWindowTitle(title)
        self.dialog_layout = QVBoxLayout()
        if self.choice.line is not None:
            if categories > 1:
                self.line_group_box = QGroupBox("Line")
            self.line_layout = QGridLayout()
            row = 0
            if self.choice.line.color is not None:
                self.line_color_label = QLabel("Color:")
                self.line_layout.addWidget(self.line_color_label, row, 0)
                self.line_color_combo = ColorComboBox(
                    self.choice.line.color,
                    no_change_values.line.color,
                    default_values.line.color
                )
                self.line_layout.addWidget(self.line_color_combo, row, 1)
                row += 1
            if self.choice.line.width is not None:
                self.line_width_label = QLabel("Width:")
                self.line_layout.addWidget(self.line_width_label, row, 0)
                self.line_width_combo = LineWidthComboBox(
                    self.choice.line.width,
                    no_change_values.line.width,
                    default_values.line.width
                )
                self.line_layout.addWidget(self.line_width_combo, row, 1)
                row += 1
            if self.choice.line.style is not None:
                self.line_style_label = QLabel("Style:")
                self.line_layout.addWidget(self.line_style_label, row, 0)
                self.line_style_combo = LineStyleComboBox(
                    self.choice.line.style,
                    no_change_values.line.style,
                    default_values.line.style
                )
                self.line_layout.addWidget(self.line_style_combo, row, 1)
                row += 1
            if categories > 1:
                self.line_group_box.setLayout(self.line_layout)
                self.dialog_layout.addWidget(self.line_group_box)
            else:
                self.dialog_layout.addLayout(self.line_layout)
        if self.choice.fill is not None:
            if categories > 1:
                self.fill_group_box = QGroupBox("Fill")
            self.fill_layout = QGridLayout()
            row = 0
            if self.choice.fill.color is not None:
                self.fill_color_label = QLabel("Color:")
                self.fill_layout.addWidget(self.fill_color_label, row, 0)
                self.fill_color_combo = ColorComboBox(
                    self.choice.fill.color,
                    no_change_values.fill.color,
                    default_values.fill.color
                )
                self.fill_layout.addWidget(self.fill_color_combo, row, 1)
                row += 1
            if self.choice.fill.style is not None:
                self.fill_style_label = QLabel("Style:")
                self.fill_layout.addWidget(self.fill_style_label, row, 0)
                self.fill_style_combo = FillStyleComboBox(
                    self.choice.fill.style,
                    no_change_values.fill.style,
                    default_values.fill.style
                )
                self.fill_layout.addWidget(self.fill_style_combo, row, 1)
                row += 1
            if categories > 1:
                self.fill_group_box.setLayout(self.fill_layout)
                self.dialog_layout.addWidget(self.fill_group_box)
            else:
                self.dialog_layout.addLayout(self.fill_layout)
        if self.choice.text is not None:
            if categories > 1:
                self.text_group_box = QGroupBox("Text")
            self.text_layout = QGridLayout()
            row = 0
            if self.choice.text.color is not None:
                self.text_color_label = QLabel("Color:")
                self.text_layout.addWidget(self.text_color_label, row, 0)
                self.text_color_combo = ColorComboBox(
                    self.choice.text.color,
                    no_change_values.text.color,
                    default_values.text.color
                )
                self.text_layout.addWidget(self.text_color_combo, row, 1)
                row += 1
            if self.choice.text.family is not None:
                self.text_family_label = QLabel("Family:")
                self.text_layout.addWidget(self.text_family_label, row, 0)
                self.text_family_combo = FontFamilyComboBox(
                    self.choice.text.family,
                    no_change_values.text.family,
                    default_values.text.family
                )
                self.text_layout.addWidget(self.text_family_combo, row, 1)
                row += 1
            if self.choice.text.size is not None:
                self.text_size_label = QLabel("Size:")
                self.text_layout.addWidget(self.text_size_label, row, 0)
                self.text_size_combo = FontSizeComboBox(
                    self.choice.text.size,
                    no_change_values.text.size,
                    default_values.text.size
                )
                self.text_layout.addWidget(self.text_size_combo, row, 1)
                row += 1
            if self.choice.text.bold is not None:
                self.text_bold_label = QLabel("Bold:")
                self.text_layout.addWidget(self.text_bold_label, row, 0)
                self.text_bold_widget = OnOffComboBox(
                    self.choice.text.bold,
                    no_change_values.text.bold,
                    default_values.text.bold
                )
                self.text_layout.addWidget(self.text_bold_widget, row, 1)
                row += 1
            if self.choice.text.italic is not None:
                self.text_italic_label = QLabel("Italic:")
                self.text_layout.addWidget(self.text_italic_label, row, 0)
                self.text_italic_widget = OnOffComboBox(
                    self.choice.text.italic,
                    no_change_values.text.italic,
                    default_values.text.italic
                )
                self.text_layout.addWidget(self.text_italic_widget, row, 1)
                row += 1
            if self.choice.text.underline is not None:
                self.text_underline_label = QLabel("Underline:")
                self.text_layout.addWidget(self.text_underline_label, row, 0)
                self.text_underline_widget = OnOffComboBox(
                    self.choice.text.underline,
                    no_change_values.text.underline,
                    default_values.text.underline
                )
                self.text_layout.addWidget(self.text_underline_widget, row, 1)
                row += 1
            if categories > 1:
                self.text_group_box.setLayout(self.text_layout)
                self.dialog_layout.addWidget(self.text_group_box)
            else:
                self.dialog_layout.addLayout(self.text_layout)
        self.setLayout(self.dialog_layout)
        self.ok_cancel_layout = QHBoxLayout()
        self.ok_cancel_layout.addStretch()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.ok_cancel_layout.addWidget(self.ok_button)
        self.ok_cancel_layout.addWidget(self.cancel_button)
        self.dialog_layout.addLayout(self.ok_cancel_layout)

    def getChoice(self : Self) -> AppearancePrefChange:
        r = AppearancePrefChange()
        if self.choice.line is not None:
            r.line = LinePrefChange()
            if self.choice.line.color is not None:
                r.line.color = self.line_color_combo.getChoice()
            if self.choice.line.width is not None:
                r.line.width = self.line_width_combo.getChoice()
            if self.choice.line.style is not None:
                r.line.style = self.line_style_combo.getChoice()
        if self.choice.fill is not None:
            r.fill = FillPrefChange()
            if self.choice.fill.color is not None:
                r.fill.color = self.fill_color_combo.getChoice()
            if self.choice.fill.style is not None:
                r.fill.style = self.fill_style_combo.getChoice()
        if self.choice.text is not None:
            r.text = TextPrefChange()
            if self.choice.text.color is not None:
                r.text.color = self.text_color_combo.getChoice()
            if self.choice.text.family is not None:
                r.text.family = self.text_family_combo.getChoice()
            if self.choice.text.size is not None:
                r.text.size = self.text_size_combo.getChoice()
            if self.choice.text.bold is not None:
                r.text.bold = self.text_bold_widget.getChoice()
            if self.choice.text.italic is not None:
                r.text.italic = self.text_italic_widget.getChoice()
            if self.choice.text.underline is not None:
                r.text.underline = self.text_underline_widget.getChoice()
        return r
