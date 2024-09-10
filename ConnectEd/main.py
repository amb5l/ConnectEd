# Block Diagram Editor application based on PyQt6
import sys
from PyQt6.QtWidgets import QApplication

from app import prefs
from main_window import MainWindow


def main():
    prefs.dwg.block.propertyOutline = True

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
