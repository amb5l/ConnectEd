from typing import Self

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QBrush, QFont, QFontMetrics, QPalette, QShowEvent
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStyle,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...ai.profile_refresh import ProfileModelsRefreshWorker
from ...ai.profiles import (
    AiProfile,
    PROVIDER_PRESETS,
    ProviderPreset,
    envKeyDisplayText,
    isEnvKeyName,
    loadProfiles,
    providerShortName,
    saveProfiles,
)
from ...ai.providers import defaultApiKeyName, defaultBaseUrl
from ...core.check import checked

from .components.layout.ok_cancel import OkCancelLayout


_COL_PROVIDER  = 0
_COL_URL       = 1
_COL_KEY_NAME  = 2
_COL_KEY_VALUE = 3
_TABLE_HEADERS = ("Provider", "URL", "Key Name", "Key Value")

_ENV_VALUE_CELL_MARGIN = 16
_ENV_VALUE_EDIT_MARGIN = 8


def _elidedText(font : QFont, text : str, width : int) -> str:
    if width <= 0 or not text:
        return text
    return QFontMetrics(font).elidedText(
        text,
        Qt.TextElideMode.ElideRight,
        width,
    )


def _elidedLineEditText(line_edit : QLineEdit, text : str) -> str:
    width = line_edit.contentsRect().width() - _ENV_VALUE_EDIT_MARGIN
    return _elidedText(line_edit.font(), text, width)


def _elidedTableCellText(
    table  : QTableWidget,
    column : int,
    font   : QFont,
    text   : str,
) -> str:
    width = table.columnWidth(column) - _ENV_VALUE_CELL_MARGIN
    return _elidedText(font, text, width)


class _EnvKeyValueLineEdit(QLineEdit):
    _env_display_text : str

    @checked
    def __init__(self, parent : QWidget | None = None) -> None:
        super().__init__(parent)
        self._env_display_text = ""
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

    def setEnvDisplayText(self, text : str) -> None:
        self._env_display_text = text
        self._refreshElidedText()

    def clearEnvDisplay(self) -> None:
        self._env_display_text = ""
        super().setText("")

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._env_display_text:
            self._refreshElidedText()

    def setText(self, text : str) -> None:
        if self.isReadOnly() and self._env_display_text:
            return
        self._env_display_text = ""
        super().setText(text)

    def _refreshElidedText(self) -> None:
        text = _elidedLineEditText(self, self._env_display_text)
        block = self.blockSignals(True)
        super().setText(text)
        self.setCursorPosition(0)
        self.home(False)
        self.blockSignals(block)

    def refreshElidedDisplay(self) -> None:
        if self._env_display_text:
            self._refreshElidedText()


def _envKeyMutedBrush(widget : QWidget, *, undefined : bool) -> QBrush:
    palette = widget.palette()
    role    = (
        QPalette.ColorRole.PlaceholderText
        if undefined
        else QPalette.ColorRole.Text
    )
    group = QPalette.ColorGroup.Disabled
    return QBrush(palette.color(group, role))


def _applyEnvKeyValueLineEdit(
    line_edit    : QLineEdit,
    api_key_name : str,
    base_palette : QPalette,
    base_font    : QFont,
) -> None:
    text, undefined = envKeyDisplayText(api_key_name)
    line_edit.setReadOnly(True)
    font = QFont(base_font)
    font.setItalic(True)
    line_edit.setFont(font)
    palette = QPalette(base_palette)
    palette.setBrush(
        QPalette.ColorRole.Text,
        _envKeyMutedBrush(line_edit, undefined = undefined),
    )
    line_edit.setPalette(palette)
    if isinstance(line_edit, _EnvKeyValueLineEdit):
        line_edit.setEnvDisplayText(text)
    else:
        line_edit.setText(_elidedLineEditText(line_edit, text))
        line_edit.setCursorPosition(0)
        line_edit.home(False)


def _resetKeyValueLineEdit(
    line_edit    : QLineEdit,
    base_palette : QPalette,
    base_font    : QFont,
) -> None:
    if isinstance(line_edit, _EnvKeyValueLineEdit):
        line_edit.clearEnvDisplay()
    line_edit.setReadOnly(False)
    line_edit.setFont(base_font)
    line_edit.setPalette(base_palette)


def _applyEnvKeyValueTableItem(
    item         : QTableWidgetItem,
    api_key_name : str,
    table        : QTableWidget,
) -> None:
    text, undefined = envKeyDisplayText(api_key_name)
    item.setData(Qt.ItemDataRole.UserRole, text)
    font = QFont(item.font())
    font.setItalic(True)
    item.setFont(font)
    item.setText(_elidedTableCellText(table, _COL_KEY_VALUE, font, text))
    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    item.setForeground(_envKeyMutedBrush(table, undefined = undefined))


def _refreshEnvKeyValueTableCells(table : QTableWidget, profiles : list[AiProfile]) -> None:
    for row, profile in enumerate(profiles):
        if not isEnvKeyName(profile.api_key_name):
            continue
        item = table.item(row, _COL_KEY_VALUE)
        if item is None:
            continue
        full = item.data(Qt.ItemDataRole.UserRole)
        if not full:
            text, _undefined = envKeyDisplayText(profile.api_key_name)
            full = text
            item.setData(Qt.ItemDataRole.UserRole, full)
        item.setText(
            _elidedTableCellText(table, _COL_KEY_VALUE, item.font(), str(full))
        )


def _resetKeyValueTableItem(item : QTableWidgetItem, table : QTableWidget) -> None:
    item.setData(Qt.ItemDataRole.UserRole, None)
    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
    font = QFont(item.font())
    font.setItalic(False)
    item.setFont(font)
    item.setForeground(table.palette().brush(QPalette.ColorRole.Text))


def _applyKeyValueDisplay(
    line_edit    : QLineEdit,
    api_key_name : str,
    base_palette : QPalette,
    base_font    : QFont,
) -> None:
    if isEnvKeyName(api_key_name):
        _applyEnvKeyValueLineEdit(
            line_edit,
            api_key_name,
            base_palette,
            base_font,
        )
    else:
        _resetKeyValueLineEdit(line_edit, base_palette, base_font)


def _applyKeyValueTableItem(
    item         : QTableWidgetItem,
    api_key_name : str,
    table        : QTableWidget,
) -> None:
    if isEnvKeyName(api_key_name):
        _applyEnvKeyValueTableItem(item, api_key_name, table)
    else:
        _resetKeyValueTableItem(item, table)


def _titleBarMinWidth(dialog : QDialog) -> int:
    """Minimum client width so the native caption is not clipped."""
    style = dialog.style()
    if style is None:
        return 0
    fm = QFontMetrics(QApplication.font())
    title_w = fm.horizontalAdvance(dialog.windowTitle())
    btn_w   = style.pixelMetric(
        QStyle.PixelMetric.PM_TitleBarButtonSize,
        None,
        dialog,
    )
    frame_w = style.pixelMetric(
        QStyle.PixelMetric.PM_DefaultFrameWidth,
        None,
        dialog,
    )
    icon_w  = style.pixelMetric(
        QStyle.PixelMetric.PM_SmallIconSize,
        None,
        dialog,
    )
    return title_w + btn_w * 3 + frame_w * 2 + icon_w + 24


def _fitDialogSize(dialog : QDialog, *, min_width : int = 480) -> None:
    """Size dialog so content and window title are not clipped."""
    dialog.ensurePolished()
    dialog.adjustSize()
    hint = dialog.sizeHint()
    min_w = max(hint.width(), _titleBarMinWidth(dialog), min_width)
    min_h = hint.height()
    dialog.setMinimumSize(min_w, min_h)
    if dialog.width() < min_w or dialog.height() < min_h:
        dialog.resize(min_w, max(dialog.height(), min_h))


class AiAddProfileDialog(QDialog):
    _preset         : QComboBox
    _api_key_name   : QLineEdit
    _api_key_value  : _EnvKeyValueLineEdit
    _url            : QLineEdit
    _size_fitted    : bool
    _refresh_worker : ProfileModelsRefreshWorker | None
    _profile        : AiProfile
    _value_font     : QFont
    _value_palette  : QPalette

    @checked
    def __init__(self : Self, parent : QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add AI Profile")
        self.setModal(True)
        self._size_fitted = False
        self._refresh_worker = None
        self._profile = AiProfile.fromPreset(PROVIDER_PRESETS[0])

        self._preset = QComboBox(self)
        for preset in PROVIDER_PRESETS:
            self._preset.addItem(preset.label, preset)
        self._preset.currentIndexChanged.connect(self._applyPreset)

        self._api_key_name = QLineEdit(self)
        self._api_key_name.textChanged.connect(self._updateKeyValueField)
        self._api_key_value = _EnvKeyValueLineEdit(self)
        self._url = QLineEdit(self)
        self._value_font = QFont(self._api_key_value.font())
        self._value_palette = QPalette(self._api_key_value.palette())

        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        form.addRow("Provider", self._preset)
        form.addRow("Key name", self._api_key_name)
        form.addRow("Key value", self._api_key_value)
        form.addRow("URL", self._url)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(OkCancelLayout(self))
        self.setLayout(layout)

        self._applyPreset(self._preset.currentIndex())

    def resizeEvent(self : Self, event) -> None:
        super().resizeEvent(event)
        if isEnvKeyName(self._api_key_name.text()):
            self._updateKeyValueField(self._api_key_name.text())

    def showEvent(self : Self, event : QShowEvent) -> None:
        super().showEvent(event)
        QTimer.singleShot(0, self._fitSizeOnce)

    def _fitSizeOnce(self : Self) -> None:
        if self._size_fitted:
            return
        self._size_fitted = True
        _fitDialogSize(self)
        self._api_key_value.refreshElidedDisplay()

    def _applyPreset(self : Self, _index : int) -> None:
        preset : ProviderPreset = self._preset.currentData()
        self._api_key_name.setText(defaultApiKeyName(preset.provider))
        self._api_key_value.clearEnvDisplay()
        self._url.setText(preset.url or defaultBaseUrl(preset.provider))
        self._updateKeyValueField(self._api_key_name.text())

    def _updateKeyValueField(self : Self, api_key_name : str) -> None:
        _applyKeyValueDisplay(
            self._api_key_value,
            api_key_name,
            self._value_palette,
            self._value_font,
        )

    def profile(self : Self) -> AiProfile:
        preset : ProviderPreset = self._preset.currentData()
        profile = AiProfile.fromPreset(preset)
        profile.api_key_name = self._api_key_name.text().strip()
        if isEnvKeyName(profile.api_key_name):
            profile.api_key_value = ""
        else:
            profile.api_key_value = self._api_key_value.text().strip()
        profile.url = self._url.text().strip()
        return profile

    def accept(self : Self) -> None:
        profile = self.profile()
        if self._refresh_worker is not None and self._refresh_worker.isRunning():
            return
        self._refresh_worker = ProfileModelsRefreshWorker([profile], self)
        self._refresh_worker.finished.connect(self._onProfileReady)
        self._refresh_worker.start()

    def _onProfileReady(self : Self, profiles : list) -> None:
        self._profile = profiles[0]
        super().accept()

    def createdProfile(self : Self) -> AiProfile:
        return self._profile


class AiProfilesDialog(QDialog):
    _profiles       : list[AiProfile]
    _table          : QTableWidget
    _loading_table  : bool
    _refresh_worker : ProfileModelsRefreshWorker | None

    @checked
    def __init__(self : Self, parent : QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("AI Profiles")
        self.setModal(True)
        self.resize(860, 360)

        self._profiles = loadProfiles()
        self._loading_table = False
        self._refresh_worker = None

        self._table = QTableWidget(0, len(_TABLE_HEADERS), self)
        self._table.setHorizontalHeaderLabels(list(_TABLE_HEADERS))
        self._table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self._table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(
            _COL_PROVIDER,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self._table.horizontalHeader().setSectionResizeMode(
            _COL_URL,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self._table.horizontalHeader().setSectionResizeMode(
            _COL_KEY_NAME,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self._table.horizontalHeader().sectionResized.connect(
            self._onTableColumnResized
        )
        self._table.cellChanged.connect(self._onCellChanged)

        add_button = QPushButton("Add…", self)
        add_button.clicked.connect(self._addProfile)
        remove_button = QPushButton("Remove", self)
        remove_button.clicked.connect(self._removeProfile)

        buttons = QHBoxLayout()
        buttons.addWidget(add_button)
        buttons.addWidget(remove_button)
        buttons.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addWidget(self._table, 1)
        layout.addLayout(buttons)
        layout.addLayout(OkCancelLayout(self))
        self.setLayout(layout)
        self.accepted.connect(self._save)

        self._rebuildTable()

    def resizeEvent(self : Self, event) -> None:
        super().resizeEvent(event)
        _refreshEnvKeyValueTableCells(self._table, self._profiles)

    def showEvent(self : Self, event : QShowEvent) -> None:
        super().showEvent(event)
        QTimer.singleShot(0, self._refreshEnvKeyValueCellsOnce)

    def _refreshEnvKeyValueCellsOnce(self : Self) -> None:
        _refreshEnvKeyValueTableCells(self._table, self._profiles)

    def _onTableColumnResized(
        self : Self,
        column : int,
        _old   : int,
        _new   : int,
    ) -> None:
        if column == _COL_KEY_VALUE:
            _refreshEnvKeyValueTableCells(self._table, self._profiles)

    def _rebuildTable(self : Self) -> None:
        self._loading_table = True
        self._table.setRowCount(len(self._profiles))
        for row, profile in enumerate(self._profiles):
            provider_item = QTableWidgetItem(providerShortName(profile.provider))
            provider_item.setFlags(
                provider_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            self._table.setItem(row, _COL_PROVIDER, provider_item)
            self._table.setItem(
                row,
                _COL_URL,
                QTableWidgetItem(profile.url),
            )
            self._table.setItem(
                row,
                _COL_KEY_NAME,
                QTableWidgetItem(profile.api_key_name),
            )
            value_item = QTableWidgetItem()
            if isEnvKeyName(profile.api_key_name):
                _applyKeyValueTableItem(value_item, profile.api_key_name, self._table)
            else:
                value_item.setText(profile.api_key_value)
                _resetKeyValueTableItem(value_item, self._table)
            self._table.setItem(row, _COL_KEY_VALUE, value_item)
        self._loading_table = False
        QTimer.singleShot(0, self._refreshEnvKeyValueCellsOnce)

    def _onCellChanged(self : Self, row : int, column : int) -> None:
        if self._loading_table or row < 0 or row >= len(self._profiles):
            return
        profile = self._profiles[row]
        if column == _COL_KEY_NAME:
            profile.api_key_name = self._cellText(row, _COL_KEY_NAME)
            value_item = self._table.item(row, _COL_KEY_VALUE)
            if value_item is None:
                value_item = QTableWidgetItem()
                self._table.setItem(row, _COL_KEY_VALUE, value_item)
            if isEnvKeyName(profile.api_key_name):
                profile.api_key_value = ""
                _applyKeyValueTableItem(value_item, profile.api_key_name, self._table)
            else:
                value_item.setText(profile.api_key_value)
                _resetKeyValueTableItem(value_item, self._table)
        elif column == _COL_KEY_VALUE:
            if not isEnvKeyName(profile.api_key_name):
                profile.api_key_value = self._cellText(row, _COL_KEY_VALUE)
        elif column == _COL_URL:
            profile.url = self._cellText(row, _COL_URL)

    def _cellText(self : Self, row : int, column : int) -> str:
        item = self._table.item(row, column)
        return item.text().strip() if item is not None else ""

    def _selectedRow(self : Self) -> int:
        rows = self._table.selectionModel().selectedRows()
        return rows[0].row() if rows else -1

    def _addProfile(self : Self) -> None:
        dialog = AiAddProfileDialog(self)
        if not dialog.exec():
            return
        profile = dialog.createdProfile()
        self._profiles.append(profile)
        self._rebuildTable()
        self._table.selectRow(len(self._profiles) - 1)

    def _removeProfile(self : Self) -> None:
        row = self._selectedRow()
        if row < 0 or row >= len(self._profiles):
            return
        profile = self._profiles[row]
        reply = QMessageBox.question(
            self,
            "Remove AI Profile",
            f"Remove {profile.displayLabel()}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        del self._profiles[row]
        self._rebuildTable()
        if self._profiles:
            self._table.selectRow(min(row, len(self._profiles) - 1))

    def accept(self : Self) -> None:
        self._syncProfilesFromTable()
        if self._refresh_worker is not None and self._refresh_worker.isRunning():
            return
        self._refresh_worker = ProfileModelsRefreshWorker(self._profiles, self)
        self._refresh_worker.finished.connect(self._onProfilesRefreshed)
        self._refresh_worker.start()

    def _syncProfilesFromTable(self : Self) -> None:
        for row, profile in enumerate(self._profiles):
            profile.api_key_name = self._cellText(row, _COL_KEY_NAME)
            if isEnvKeyName(profile.api_key_name):
                profile.api_key_value = ""
            else:
                profile.api_key_value = self._cellText(row, _COL_KEY_VALUE)
            profile.url = self._cellText(row, _COL_URL)

    def _onProfilesRefreshed(self : Self, profiles : list) -> None:
        self._profiles = profiles
        super().accept()

    def _save(self : Self) -> None:
        saveProfiles(self._profiles)
