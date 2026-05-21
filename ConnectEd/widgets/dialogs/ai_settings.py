from typing import Self

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from ...ai.providers import list_providers
from ...app import settings
from ...core.check import checked

from .components.layout.ok_cancel import OkCancelLayout


class AiSettingsDialog(QDialog):
    _provider : QComboBox
    _model    : QLineEdit
    _api_key  : QLineEdit
    _base_url : QLineEdit

    @checked
    def __init__(self : Self, parent : QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("AI Settings")
        self.setModal(True)

        self._provider = QComboBox(self)
        for name in sorted(list_providers()):
            self._provider.addItem(name, name)
        current = settings().get("ai/provider")
        index = self._provider.findData(current)
        if index >= 0:
            self._provider.setCurrentIndex(index)

        self._model = QLineEdit(settings().get("ai/model"), self)
        self._api_key = QLineEdit(settings().get("ai/api_key"), self)
        self._api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self._base_url = QLineEdit(settings().get("ai/base_url"), self)

        form = QFormLayout()
        form.addRow("Provider", self._provider)
        form.addRow("Model", self._model)
        form.addRow("API key", self._api_key)
        form.addRow("Base URL", self._base_url)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(OkCancelLayout(self))
        self.setLayout(layout)
        self.accepted.connect(self._save)

    def _save(self : Self) -> None:
        settings().set("ai/provider", self._provider.currentData())
        settings().set("ai/model", self._model.text())
        settings().set("ai/api_key", self._api_key.text())
        settings().set("ai/base_url", self._base_url.text())
