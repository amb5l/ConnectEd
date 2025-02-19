import sys

from PyQt6.QtWidgets import QApplication

from .core                import logger
from .widgets.main_window import MainWindow


def main():
    logger.info("started")
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    r = app.exec()
    logger.info("finished")
    return r

if __name__ == '__main__':
    r = main()
    logger.info(f"exited with code {r}")
    sys.exit(r)
