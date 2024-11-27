import sys
from PyQt6.QtWidgets import QApplication
from enum import Enum, auto

from common   import logger, untitled_number
from args     import args
from settings import settings, startup, prefs, themes, sheet_sizes
from window   import MainWindow
from diagram  import Diagram


def main():
    class FileOperation(Enum):
        NEW    = auto()
        OPEN   = auto()
        IMPORT = auto()

    logger.info('started')

    if args.reset:
        settings.reset()
    settings.load()
    if args.dump_settings:
        print('startup:')
        settings.dump(startup)
        print('prefs:')
        settings.dump(prefs)
        print('themes:')
        settings.dump(themes)
        print('sheet_sizes:')
        settings.dump(sheet_sizes)

    diagram = Diagram()
    if args.ifile:
        diagram.load(args.ifile)
    else:
        diagram.new('Untitled' + str(untitled_number))

    if args.mode == 'gui':
        app = QApplication(sys.argv)
        window = MainWindow(diagram)
        window.show()
        sys.exit(app.exec())

    logger.info('finished')

if __name__ == "__main__":
    main()
