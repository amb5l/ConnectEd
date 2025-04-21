from typing import Self

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import \
    QWidget, QTextEdit, QPlainTextEdit, \
    QHBoxLayout, QLabel, QComboBox, QToolButton, QCheckBox
from PyQt6.QtGui import QIcon, QTextDocument


class FindBar(QWidget):
    text_edit   : QPlainTextEdit
    find_label  : QLabel
    find_combo  : QComboBox
    find_prev   : QToolButton
    find_next   : QToolButton
    match_case  : QCheckBox
    whole_words : QCheckBox
    highlight   : QCheckBox

    def __init__(self : Self, parent : QWidget, text_edit : QPlainTextEdit) -> None:
        super().__init__(parent)
        self.text_edit = text_edit

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)

        self.find_label = QLabel("Find:")
        layout.addWidget(self.find_label)

        self.find_combo = QComboBox()
        self.find_combo.setEditable(True)
        self.find_combo.setMaxCount(10)  # remember last 10 searches
        self.find_combo.setMinimumWidth(150)
        layout.addWidget(self.find_combo)

        self.find_prev = QToolButton()
        self.find_prev.setIcon(QIcon(QIcon.fromTheme("go-previous")))
        self.find_prev.setToolTip("Find Previous")
        self.find_next = QToolButton()
        self.find_next.setIcon(QIcon(QIcon.fromTheme("go-next")))
        self.find_next.setToolTip("Find Next")
        layout.addWidget(self.find_prev)
        layout.addWidget(self.find_next)

        self.match_case = QCheckBox()
        self.match_case.setText("&Match Case")
        layout.addWidget(self.match_case)

        self.whole_words = QCheckBox()
        self.whole_words.setText("&Whole Words")
        layout.addWidget(self.whole_words)

        self.highlight = QCheckBox()
        self.highlight.setText("Highlight")
        layout.addWidget(self.highlight)

        layout.addStretch()

        self.setLayout(layout)

        # connect signals
        self.find_combo.lineEdit().returnPressed.connect(lambda: self.slotFind(forward=True))
        self.find_next.clicked.connect(lambda: self.slotFind(forward=True))
        self.find_prev.clicked.connect(lambda: self.slotFind(forward=False))
        self.highlight.toggled.connect(self.slotHighlight)

    def slotFind(self : Self, forward : bool = True) -> bool:
        """Find the next/previous occurrence of the search text."""
        text = self.find_combo.currentText()
        if not text:
            return False

        # Add to search history if not already present
        if self.find_combo.findText(text) == -1:
            self.find_combo.addItem(text)

        # Set up find flags
        flags = QTextDocument.FindFlag(0)
        if self.match_case.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if self.whole_words.isChecked():
            flags |= QTextDocument.FindFlag.FindWholeWords
        if not forward:
            flags |= QTextDocument.FindFlag.FindBackward

        # Perform the search
        found = self.text_edit.find(text, flags)

        if not found and self.text_edit.textCursor().atEnd():
            # Wrap around to beginning/end
            cursor = self.text_edit.textCursor()
            cursor.movePosition(
                cursor.MoveOperation.Start if forward else cursor.MoveOperation.End
            )
            self.text_edit.setTextCursor(cursor)
            found = self.text_edit.find(text, flags)

        return found

    def slotHighlight(self : Self, enabled : bool) -> None:
        """Update all matching text highlights."""
        if not enabled:
            # Clear all highlights
            self.text_edit.setExtraSelections([])
            return

        text = self.find_combo.currentText()
        if not text:
            return

        # Save current cursor
        current_cursor = self.text_edit.textCursor()

        # Move to start
        cursor = self.text_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        self.text_edit.setTextCursor(cursor)

        # Set up find flags
        flags = QTextDocument.FindFlag(0)
        if self.match_case.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if self.whole_words.isChecked():
            flags |= QTextDocument.FindFlag.FindWholeWords

        # Find all occurrences
        extra_selections = []
        while self.text_edit.find(text, flags):
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(Qt.GlobalColor.yellow)
            selection.cursor = self.text_edit.textCursor()
            extra_selections.append(selection)

        # Restore cursor and apply highlights
        self.text_edit.setTextCursor(current_cursor)
        self.text_edit.setExtraSelections(extra_selections)
