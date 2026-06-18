from typing import Self

from PyQt6.QtWidgets import QMdiSubWindow, QWidget

from ...core.doc   import DocBinding


class DocSubWindow(QMdiSubWindow):
    _binding : DocBinding | None

    def __init__(
        self    : Self,
        parent  : QWidget    | None = None,
        binding : DocBinding | None = None,

    ) -> None:
        super().__init__(parent)
        self._binding = binding

    def docBinding(self : Self) -> DocBinding | None:
        return self._binding
