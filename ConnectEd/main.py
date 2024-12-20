import sys
from PyQt6.QtWidgets import QApplication
from enum import Enum, auto

from log      import logger
from args     import args, unknown_args
from settings import settings

from main_window import MainWindow
from canvas      import Canvas
from diagram     import Diagram


def main():
    logger.info('started')
    if args.reset:
        settings.reset()
    settings.load()
    if args.dump_settings:
        print('startup:')
        settings.dump(settings.startup)
        print('prefs:')
        settings.dump(settings.prefs)
        print('themes:')
        settings.dump(settings.themes)
        print('sheet_sizes:')
        settings.dump(settings.sheet_sizes)

    if args.mode == 'gui':
        app = QApplication(sys.argv[:1] + unknown_args)
        main_window = MainWindow()
        main_window.show()
        # TODO handle multiple input files
        if args.ifile:
            main_window.fileOpen(args.ifile)
        else:
            main_window.fileNew()
        sys.exit(app.exec())
    elif args.mode == 'cmd':
        if args.ifile:
            diagram = Diagram()
            diagram.fileOpen(args.ifile)
            print("TODO: implement command line processing")
    else:
        logger.error(f'unknown application UI mode: {args.mode}')

    logger.info('finished')

if __name__ == "__main__":
    main()
