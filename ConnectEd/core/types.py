from PyQt6.QtCore   import QObject
from PyQt6.QtGui    import QAction, QKeySequence, QFont

class Action(QAction):
    def __init__(
        self      : 'Action',
        parent    : QObject,
        text      : str,
        tooltip   : str,
        shortcut  : QKeySequence | str | None,
        checkable : bool = False,
        checked   : bool = False
    ) -> None:
        super().__init__(parent)
        self.setText(text)
        self.setToolTip(tooltip)
        if shortcut is not None:
            self.setShortcut(shortcut)
        self.setCheckable(checkable)
        if checkable:
            self.setChecked(checked)

class FontSpec:
    def __init__(
        self   : 'FontSpec',
        family : str,
        size   : int,
        bold   : bool,
        italic : bool
    ) -> None:
        self.family = family
        self.size   = size
        self.bold   = bold
        self.italic = italic

    @classmethod
    def __initFromStr__(cls, s: str) -> 'FontSpec':
        family, size, bold, italic = s.split(',')
        size = int(float(size))
        bold = bold == 'True'
        italic = italic == 'True'
        return cls(family, size, bold, italic)

    def __str__(self: 'FontSpec') -> str:
        return f'{self.family},{self.size},{self.bold},{self.italic}'

    def toQFont(self: 'FontSpec') -> QFont:
        return QFont(
            self.family,
            self.size,
            QFont.Weight.Bold if self.bold else QFont.Weight.Normal,
            self.italic
        )
