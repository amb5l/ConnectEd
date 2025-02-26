import sys

from PyQt6.QtWidgets import QApplication

from .core                import logger, args, unknown_args, settings
from .widgets.main_window import MainWindow
from .resources           import initResources


def main():
    logger.info("started")
    if args.reset:
        settings.reset()
    settings.load()
    print(settings.dump())
    app = QApplication(sys.argv[:1] + unknown_args)
    initResources()
    main_window = MainWindow()
    main_window.show()
    r = app.exec()
    settings.save()
    logger.info("finished")
    return r

if __name__ == '__main__':
    r = main()
    logger.info(f"exited with code {r}")
    sys.exit(r)
