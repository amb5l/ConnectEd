from typing import Self

from PyQt6.QtCore    import Qt, QSize, QTimer
from PyQt6.QtWidgets import QWidget, QDialog, QColorDialog, \
                            QLabel, QComboBox, QLineEdit, \
                            QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt6.QtGui     import QPainter, QColor, QPen, QBrush, \
                            QPixmap, QIcon, QFontDatabase, QFont, \
                            QIntValidator, QDoubleValidator

from ...core.utils import val2str

from ...core.icon import getDefaultIconSize, getFgBgColors, \
                         SvgIconSingleton, CharIconSingleton

from ...resources import getIconPath

from ..graphics.items import Default, DEFAULT, NoChange, NO_CHANGE, Edge, \
                             LinePref, LinePrefChange, \
                             FillPref, FillPrefChange, \
                             QuillSpec, QuillPref, QuillPrefChange

from . import okCancelLayout


CUSTOM_ICON_SIZE = QSize(getDefaultIconSize() * 2, getDefaultIconSize())


class NoChangeIcon(SvgIconSingleton):
    PATH = getIconPath("no_change.svg")
    SIZE = CUSTOM_ICON_SIZE


class DefaultIcon(SvgIconSingleton):
    PATH = getIconPath("default.svg")
    SIZE = CUSTOM_ICON_SIZE


class QueryIcon(CharIconSingleton):
    FONT_FAMILY = "Arial"
    CHAR = "?"
    SIZE = CUSTOM_ICON_SIZE


class CustomColorDialog(QColorDialog):
    def __init__(
        self   : Self,
        color  : QColor,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Color")
        self.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
        if isinstance(color, QColor):
            self.setCurrentColor(color)
        self._html_box = None
        self._find_html_box()
        self.currentColorChanged.connect(self._on_color_changed)

    def _find_html_box(self : Self) -> None:
        for line_edit in self.findChildren(QLineEdit):
            if line_edit.text().startswith("#"):
                self._html_box = line_edit
                line_edit.textChanged.connect(self._on_html_text_changed)
                self._make_uppercase()
                return
        # If not found yet, try again after a short delay (dialog might still be initializing)
        if self._html_box is None:
            QTimer.singleShot(100, self._find_html_box)

    def _make_uppercase(self : Self) -> None:
        if self._html_box:
            current_text = self._html_box.text()
            if current_text.startswith("#") and current_text != current_text.upper():
                self._html_box.textChanged.disconnect(self._on_html_text_changed)
                self._html_box.setText(current_text.upper())
                self._html_box.textChanged.connect(self._on_html_text_changed)

    def _on_color_changed(self : Self, color : QColor) -> None:
        QTimer.singleShot(10, self._make_uppercase)

    def _on_html_text_changed(self : Self, text : str) -> None:
        if text.startswith("#") and text != text.upper():
            self._make_uppercase()

    def getChoice(self : Self) -> QColor | None:
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

    choice : NoChange | Default | QColor | None

    def __init__(
        self      : Self,
        initial   : NoChange | Default | QColor,
        default   : Default | QColor,
        no_change : NoChange | Default | QColor | None = None,
        parent    : QWidget | None = None
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
            self.setItemText(custom_idx, f"<custom = {val2str(initial)}>")
        self.choice = initial
        self.activated.connect(self.onActivated)

    def onActivated(self : Self, index : int) -> None:
        selected_text = self.currentText()
        if selected_text == "<no change>":
            self.choice = NO_CHANGE
        elif selected_text == "<default>":
            self.choice = DEFAULT
        elif selected_text.startswith("<custom"):
            dialog = CustomColorDialog(
                self.choice if isinstance(self.choice, QColor) else None,
                parent=self
            )
            if dialog.exec():
                self.choice = dialog.getChoice()
                self.setItemIcon(index, self.getIcon(self.choice))
                self.setItemText(index, f"<custom = {val2str(self.choice)}>")
        else:
            self.choice = self.COLORS[selected_text]

    def getIcon(self : Self, color : QColor) -> QIcon:
        size = self.iconSize()
        pixmap = QPixmap(size.width(), size.height())
        pixmap.fill(color)
        with QPainter(pixmap) as painter:
            painter.fillRect(0, 0, size.width(), size.height(), color)
        return QIcon(pixmap)

    def getChoice(self : Self) -> NoChange | Default | QColor | None:
        return self.choice


class CustomLineWidthDialog(QDialog):
    def __init__(
        self    : Self,
        initial : float | int | None = None,
        parent  : QWidget | None = None
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

    def getChoice(self : Self) -> float | None:
        try:
            return float(self.width_input.text())
        except ValueError:
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
        no_change : NoChange | Default | float | int | None = None,
        parent    : QWidget | None = None
    ) -> None:
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
            dialog = CustomLineWidthDialog(parent=self)
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

    def getChoice(self : Self) -> float | None | NoChange:
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
            except ValueError:
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
        no_change : NoChange | Default | Qt.PenStyle | None = None,
        parent    : QWidget | None = None
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

    def getChoice(self : Self) -> NoChange | Default | Qt.PenStyle | None:
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
        no_change : NoChange | Default | Qt.BrushStyle | None = None,
        parent    : QWidget | None = None
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

    def getChoice(self : Self) -> NoChange | Default | Qt.PenStyle | None:
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
        no_change : NoChange | Default | str | None = None,
        parent    : QWidget | None = None
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

    def getChoice(self : Self) -> NoChange | Default | str:
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
        no_change : NoChange | Default | float | int | None = None,
        parent    : QWidget | None = None
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
            size_str = str(int(initial) if initial == int(initial) else initial)
            if size_str in self.sizes:
                self.setCurrentIndex(self.sizes.index(size_str))
            else:
                self.setCurrentIndex(default_idx)

    def getChoice(self : Self) -> NoChange | Default | float | None:
        text = self.currentText()
        if text.startswith("<no change"):
            return NO_CHANGE
        elif text.startswith("<default"):
            return DEFAULT
        else:
            try:
                return float(text)
            except ValueError:
                return None


class OnOffComboBox(QComboBox):
    def __init__(
        self      : Self,
        initial   : NoChange | Default | bool,
        default   : Default | bool,
        no_change : NoChange | Default | bool | None = None,
        parent    : QWidget | None = None
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

    def getChoice(self : Self) -> NoChange | Default | bool | None:
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
        no_change : LinePrefChange | None = None,
        parent    : QWidget | None = None
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
        no_change : FillPrefChange | None = None,
        parent    : QWidget | None = None
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
        no_change : QuillPrefChange | None = None,
        parent    : QWidget | None = None
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


class EdgeComboBox(QComboBox):
    def __init__(self : Self,
        edge   : Edge,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.addItems([e.value for e in Edge])

    def getChoice(self : Self) -> Edge:
        return Edge(self.currentText())


class StringEdit(QLineEdit):
    def __init__(self : Self, value : str, parent=None):
        super().__init__(parent)
        self.setText(value)


class IntEdit(QLineEdit):
    def __init__(self : Self, value : int, parent=None):
        super().__init__(parent)
        self.setValidator(QIntValidator())
        self.setText(str(value))

    def setValue(self : Self, value : int) -> None:
        self.setText(str(value))

    def getValue(self : Self) -> int:
        try:
            return int(self.text())
        except ValueError:
            return 0


class FloatEdit(QLineEdit):
    def __init__(self : Self, value : float, parent=None):
        super().__init__(parent)
        self.setValidator(QDoubleValidator())
        self.setValue(value)

    def setValue(self : Self, value : float) -> None:
        self.setText(str(value))

    def getValue(self : Self) -> float:
        try:
            return float(self.text())
        except ValueError:
            return 0.0
