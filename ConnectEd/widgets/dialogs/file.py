from PyQt6.QtWidgets import QFileDialog, QWidget

from ...core.defs import GEN_EXT, LIB_EXT, DSN_EXT


class FileOpenDialog(QFileDialog):
    def __init__(
        self      : "FileOpenDialog",
        type_name : str | None = None,
        parent    : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Open")
        self.setFileMode(QFileDialog.FileMode.ExistingFiles)
        match type_name:
            case None:
                self.setNameFilter(f"Connected Files (*{GEN_EXT});;All Files (*.*)`")
            case "DesignDb":
                self.setNameFilter(f"Connected Designs (*{DSN_EXT});;Connected Libraries (*{LIB_EXT});;Connected Files (*{GEN_EXT});;All Files (*.*)")
            case "LibraryDb":
                self.setNameFilter(f"Connected Libraries (*{LIB_EXT});;Connected Designs (*{DSN_EXT});;Connected Files (*{GEN_EXT});;All Files (*.*)")
            case _:
                raise ValueError(f"Unknown type name: {type_name}")
        self.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)

class FileSaveAsDialog(QFileDialog):
    def __init__(
        self      : "FileSaveAsDialog",
        type_name : str,
        parent    : QWidget | None = None
    ) -> None:
        match type_name:
            case "LibraryDb":
                name_filter    = f"Connected Libraries ({LIB_EXT})"
                default_suffix = LIB_EXT
            case "DesignDb":
                name_filter    = f"Connected Designs ({DSN_EXT})"
                default_suffix = DSN_EXT
            case _:
                raise ValueError(f"Unknown type name: {type_name}")
        super().__init__(parent)
        self.setWindowTitle(f"Save {type_name} As")
        self.setFileMode(QFileDialog.FileMode.AnyFile)
        self.setNameFilter(name_filter)
        self.setDefaultSuffix(default_suffix)
        self.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
