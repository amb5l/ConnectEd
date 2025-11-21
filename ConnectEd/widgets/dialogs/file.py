from PyQt6.QtWidgets import QFileDialog, QWidget

from ...core.defs import LIB_EXT, DSN_EXT


class FileOpenDialog(QFileDialog):
    def __init__(
        self   : "FileOpenDialog",
        kind   : str | None = None,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Open")
        self.setFileMode(QFileDialog.FileMode.ExistingFiles)
        match kind:
            case None:
                self.setNameFilter(f"All Files (*.*)")
            case "Design":
                self.setNameFilter(f"Connected Designs (*{DSN_EXT});;Connected Libraries (*{LIB_EXT});;All Files (*.*)")
            case "Library":
                self.setNameFilter(f"Connected Libraries (*{LIB_EXT});;Connected Designs (*{DSN_EXT});;All Files (*.*)")
            case _:
                raise ValueError(f"Unknown type name: {kind}")
        self.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)


class FileSaveAsDialog(QFileDialog):
    def __init__(
        self   : "FileSaveAsDialog",
        kind   : str,
        parent : QWidget | None = None
    ) -> None:
        match kind:
            case "Design":
                name_filter    = f"Connected Designs (*{DSN_EXT})"
                default_suffix = DSN_EXT
            case "Library":
                name_filter    = f"Connected Libraries (*{LIB_EXT})"
                default_suffix = LIB_EXT
            case _:
                raise ValueError(f"Unknown type name: {kind}")
        super().__init__(parent)
        self.setWindowTitle(f"Save {kind} As")
        self.setFileMode(QFileDialog.FileMode.AnyFile)
        self.setNameFilter(name_filter)
        self.setDefaultSuffix(default_suffix)
        self.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
