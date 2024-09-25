# Block Diagram Editor application based on PyQt6
# TODO: handle command line arguments - including batch (non-GUI) operation

import sys, logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor

from common import logger
#from args.args import Args
from prefs.prefs import prefs
from window.window import MainWindow
from diagram.diagram import Diagram


def main():
    logger.info('started')
    #args = Args()
    prefs().draw.block.property.outline = True
    untitledNumber = 1
    # create a new diagram
    diagram = Diagram(prefs().general.untitled + str(untitledNumber))
    app = QApplication(sys.argv)
    window = MainWindow(diagram)
    window.show()
    sys.exit(app.exec())
    logger.info('finished')

if __name__ == "__main__":
    main()
