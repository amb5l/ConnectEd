# Block Diagram Editor application based on PyQt6
# TODO: handle command line arguments - including batch (non-GUI) operation

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor

from prefs import prefs
from main_window import MainWindow
from diagram.diagram import Diagram


def main():
    prefs.dwg.block.property.line = prefs.Dwg.Line(QColor(255,255,255))

    untitledNumber = 1
    diagram = Diagram("Untitled" + str(untitledNumber))

    app = QApplication(sys.argv)
    window = MainWindow(diagram)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
