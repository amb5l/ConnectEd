# Block Diagram Editor application based on PyQt6
# TODO: handle command line arguments - including batch (non-GUI) operation

import sys
from PyQt6.QtWidgets import QApplication

from app import prefs
from main_window import MainWindow
from diagram import Diagram


def main():
    prefs.dwg.block.propertyOutline = True

    untitledNumber = 1
    diagram = Diagram("Untitled" + str(untitledNumber))

    app = QApplication(sys.argv)
    window = MainWindow(diagram)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
