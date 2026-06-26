"""Background worker to fetch model lists for AI profiles."""

from __future__ import annotations

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QWidget

from ..core.check import checked

from .profile_models import refreshAllProfileModels
from .profiles import AiProfile


class ProfileModelsRefreshWorker(QThread):
    finished = pyqtSignal(list)

    _profiles : list[AiProfile]

    @checked
    def __init__(
        self,
        profiles : list[AiProfile],
        parent   : QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._profiles = profiles

    def run(self) -> None:
        refreshAllProfileModels(self._profiles)
        self.finished.emit(self._profiles)
