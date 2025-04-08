import sys

from PyQt6.QtWidgets import QApplication

from .core      import logger, known_args, unknown_args, \
                       NameCounter, Settings, DbModel
from .widgets   import MainWindow
from .resources import initResources

from . import hub


def main() -> int:
    logger.info("started")
    hub.name_counter = NameCounter()
    hub.settings = Settings()
    if known_args.reset:
        hub.settings.reset()
    hub.settings.load()
    print(hub.settings.dump())
    app = QApplication(sys.argv[:1] + unknown_args)
    app.setStyle('Fusion')
    initResources()
    hub.db_model = DbModel()
    hub.main_window = MainWindow()
    hub.main_window.show()
    r = app.exec()
    hub.settings.save()
    logger.info("finished")
    return r

if __name__ == '__main__':
    r = main()
    logger.info(f"exited with code {r}")
    sys.exit(r)
