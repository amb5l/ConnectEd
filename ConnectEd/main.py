# Block Diagram Editor application based on PyQt6
# TODO: handle command line arguments - including batch (non-GUI) operation

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor
from enum import Enum, auto

from common import logger
#from args.args import Args
from prefs.prefs import prefs
from window.window import MainWindow
from diagram.diagram import Diagram


def main():
    class RunMode(Enum):
        GUI = auto() # GUI
        CMD = auto() # command line

    class FileOperation(Enum):
        NEW    = auto()
        OPEN   = auto()
        IMPORT = auto()

    logger.info('started')

    #args = Args()
    runMode = RunMode.GUI
    fileOperation = FileOperation.NEW
    fileName = None

    untitledNumber = 1

    match fileOperation:
        case FileOperation.NEW:
            diagram = Diagram(
                'Untitled' + str(untitledNumber), #
                prefs.file.new.sheetSize
            )
        case FileOperation.OPEN:
            diagram = Diagram()
            diagram.fileOpen(fileName)
        case FileOperation.IMPORT:
            diagram = Diagram()
            diagram.fileImport(fileName)
        case _:
            pass # TODO: error message

    match runMode:
        case RunMode.CMD:
            pass # TODO: batch mode
        case RunMode.GUI:
            app = QApplication(sys.argv)
            window = MainWindow(diagram)
            window.show()
            sys.exit(app.exec())
        case _:
            pass # TODO: error message (unsupported run mode)

    logger.info('finished')

if __name__ == "__main__":
    main()
