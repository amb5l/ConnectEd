import sys

from PyQt6.QtWidgets import QApplication

from .core      import logger, known_args, unknown_args, settings
from .widgets   import MainWindow
from .resources import initResources

from . import hub


def main() -> int:
    logger.info("started")
    if known_args.reset:
        settings.reset()
    settings.load()
    #print(settings.dump())
    app = QApplication(sys.argv[:1] + unknown_args)
    initResources()
    hub.main_window = MainWindow()
    hub.main_window.show()
    r = app.exec()
    settings.save()
    logger.info("finished")
    return r

if __name__ == '__main__':
    r = main()
    logger.info(f"exited with code {r}")
    sys.exit(r)
