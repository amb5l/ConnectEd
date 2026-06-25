from typing import Self

from PyQt6.QtWidgets import QMdiSubWindow, QWidget
from PyQt6.QtGui     import QCloseEvent

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

    def closeEvent(self : Self, event : QCloseEvent) -> None:
        # ensure binding is valid
        binding = self.docBinding()
        if binding is None:
            event.accept()
            return
        # get doc
        doc = binding.doc
        # allow doc to prompt for commit/discard, and veto if necessary
        if not doc.closeSubWindow(self):
            event.ignore()
            return
        # allow doc to clean up (after accepted, before destruction)
        doc.onSubWindowClosed(self)
        # done
        super().closeEvent(event)

    def docBinding(self : Self) -> DocBinding | None:
        return self._binding
