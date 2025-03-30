__all__ = ['FileSaveAsDialog']

from PyQt6.QtWidgets import QFileDialog

from ...core import LIB_EXT, DSN_EXT
from .. import MainWindow

class FileSaveAsDialog(QFileDialog):
    def __init__(
        self        : 'FileSaveAsDialog',
        main_window : MainWindow,
        type_name   : str
    ) -> None:
        match type_name:
            case 'Library':
                name_filter    = f'Connected Libraries ({LIB_EXT})'
                default_suffix = LIB_EXT
            case 'Design':
                name_filter    = f'Connected Designs ({DSN_EXT})'
                default_suffix = DSN_EXT
            case _:
                raise ValueError(f'Unknown type name: {type_name}')
        name_filter += '; All ConnectEd Files (*.ce*); All Files (*)'
        super().__init__(main_window)
        self.setWindowTitle('Save As')
        self.setFileMode(QFileDialog.FileMode.AnyFile)
        self.setNameFilter(name_filter)
        self.setDefaultSuffix(default_suffix)
        self.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
